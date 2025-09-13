from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.template import Template, Context
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from typing import Optional, Dict, Any, List
import json

from .models import Notification, NotificationType, NotificationPriority, NotificationSettings, NotificationTemplate


class NotificationService:
    """Сервис для отправки уведомлений"""
    
    @staticmethod
    def create_notification(
        recipient: User,
        notification_type: str,
        title: str,
        message: str,
        sender: Optional[User] = None,
        priority: str = NotificationPriority.NORMAL,
        related_object_id: Optional[int] = None,
        related_object_type: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """Создать уведомление"""
        
        # Получаем настройки пользователя
        settings_obj, created = NotificationSettings.objects.get_or_create(user=recipient)
        
        # Проверяем, нужно ли отправлять уведомление
        if not NotificationService._should_send_notification(notification_type, settings_obj):
            return None
        
        # Создаем уведомление
        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type=notification_type,
            priority=priority,
            title=title,
            message=message,
            related_object_id=related_object_id,
            related_object_type=related_object_type,
            extra_data=extra_data or {}
        )
        
        # Отправляем email если нужно
        if NotificationService._should_send_email(notification_type, settings_obj):
            NotificationService._send_email_notification(notification)
        
        return notification
    
    @staticmethod
    def _should_send_notification(notification_type: str, settings: NotificationSettings) -> bool:
        """Проверить, нужно ли отправлять уведомление"""
        if notification_type.startswith('consultation_'):
            return settings.email_consultations or settings.push_consultations
        elif notification_type.startswith('forum_'):
            return settings.email_forum or settings.push_forum
        elif notification_type.startswith('review_'):
            return settings.email_reviews or settings.push_reviews
        elif notification_type.startswith('blog_'):
            return settings.email_blog or settings.push_blog
        elif notification_type.startswith('system_'):
            return settings.email_system or settings.push_system
        elif notification_type.startswith('tracker_'):
            return settings.email_tracker or settings.push_tracker
        else:
            return True
    
    @staticmethod
    def _should_send_email(notification_type: str, settings: NotificationSettings) -> bool:
        """Проверить, нужно ли отправлять email"""
        if not settings.email_enabled:
            return False
        
        if notification_type.startswith('consultation_'):
            return settings.email_consultations
        elif notification_type.startswith('forum_'):
            return settings.email_forum
        elif notification_type.startswith('review_'):
            return settings.email_reviews
        elif notification_type.startswith('blog_'):
            return settings.email_blog
        elif notification_type.startswith('system_'):
            return settings.email_system
        elif notification_type.startswith('tracker_'):
            return settings.email_tracker
        else:
            return True
    
    @staticmethod
    def _send_email_notification(notification: Notification):
        """Отправить email уведомление"""
        try:
            send_mail(
                subject=f"[BaybyWay] {notification.title}",
                message=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.recipient.email],
                fail_silently=False,
            )
            notification.is_email_sent = True
            notification.save(update_fields=['is_email_sent'])
        except Exception as e:
            print(f"Ошибка отправки email: {e}")
    
    @staticmethod
    def send_consultation_notification(
        recipient: User,
        consultation,
        notification_type: str,
        sender: Optional[User] = None
    ):
        """Отправить уведомление о консультации"""
        if notification_type == NotificationType.CONSULTATION_REQUEST:
            title = "Новый запрос на консультацию"
            message = f"Получен новый запрос на консультацию от {consultation.parent.get_full_name()}"
        elif notification_type == NotificationType.CONSULTATION_ACCEPTED:
            title = "Консультация принята"
            message = f"Ваш запрос на консультацию к {consultation.doctor.get_full_name()} принят"
        elif notification_type == NotificationType.CONSULTATION_REJECTED:
            title = "Консультация отклонена"
            message = f"Ваш запрос на консультацию к {consultation.doctor.get_full_name()} отклонен"
        elif notification_type == NotificationType.CONSULTATION_COMPLETED:
            title = "Консультация завершена"
            message = f"Консультация с {consultation.doctor.get_full_name()} завершена"
        elif notification_type == NotificationType.CONSULTATION_MESSAGE:
            title = "Новое сообщение в консультации"
            message = f"Новое сообщение в консультации с {consultation.doctor.get_full_name()}"
        else:
            return
        
        return NotificationService.create_notification(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            sender=sender,
            related_object_id=consultation.id,
            related_object_type='consultation'
        )
    
    @staticmethod
    def send_forum_notification(
        recipient: User,
        topic,
        notification_type: str,
        sender: Optional[User] = None
    ):
        """Отправить уведомление о форуме"""
        if notification_type == NotificationType.FORUM_TOPIC_REPLY:
            title = "Новый ответ в теме форума"
            message = f"Новый ответ в теме '{topic.title}'"
        elif notification_type == NotificationType.FORUM_TOPIC_CREATED:
            title = "Новая тема в форуме"
            message = f"Создана новая тема '{topic.title}' в категории {topic.category.name}"
        elif notification_type == NotificationType.FORUM_TOPIC_SOLUTION:
            title = "Тема отмечена как решение"
            message = f"Ваша тема '{topic.title}' отмечена как решение"
        elif notification_type == NotificationType.FORUM_TOPIC_DELETED:
            title = "Тема удалена"
            message = f"Тема '{topic.title}' была удалена модератором"
        else:
            return
        
        return NotificationService.create_notification(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            sender=sender,
            related_object_id=topic.id,
            related_object_type='forum_topic'
        )
    
    @staticmethod
    def send_forum_topic_reply_notification(
        topic,
        post,
        sender: User
    ):
        """Отправить уведомления о новом ответе в теме всем подписчикам"""
        from forum.models import TopicSubscription
        
        # Получаем всех подписчиков темы (кроме автора сообщения)
        subscribers = TopicSubscription.objects.filter(
            topic=topic,
            is_active=True
        ).exclude(user=sender).select_related('user')
        
        notifications = []
        for subscription in subscribers:
            notification = NotificationService.create_notification(
                recipient=subscription.user,
                notification_type=NotificationType.FORUM_TOPIC_REPLY,
                title=f"Новый ответ в теме '{topic.title}'",
                message=f"Пользователь {sender.get_full_name() or sender.username} ответил в теме '{topic.title}'",
                sender=sender,
                related_object_id=topic.id,
                related_object_type='forum_topic',
                extra_data={
                    'topic_id': topic.id,
                    'post_id': post.id,
                    'topic_title': topic.title,
                    'category_name': topic.category.name
                }
            )
            if notification:
                notifications.append(notification)
        
        return notifications
    
    @staticmethod
    def send_forum_topic_created_notification(
        topic,
        sender: User
    ):
        """Отправить уведомления о новой теме всем подписчикам категории"""
        from forum.models import CategorySubscription
        
        # Получаем всех подписчиков категории (кроме автора темы)
        subscribers = CategorySubscription.objects.filter(
            category=topic.category,
            is_active=True
        ).exclude(user=sender).select_related('user')
        
        notifications = []
        for subscription in subscribers:
            notification = NotificationService.create_notification(
                recipient=subscription.user,
                notification_type=NotificationType.FORUM_TOPIC_CREATED,
                title=f"Новая тема в категории '{topic.category.name}'",
                message=f"Пользователь {sender.get_full_name() or sender.username} создал новую тему '{topic.title}' в категории '{topic.category.name}'",
                sender=sender,
                related_object_id=topic.id,
                related_object_type='forum_topic',
                extra_data={
                    'topic_id': topic.id,
                    'topic_title': topic.title,
                    'category_name': topic.category.name
                }
            )
            if notification:
                notifications.append(notification)
        
        return notifications
    
    @staticmethod
    def send_forum_post_quoted_notification(
        quoted_user: User,
        topic,
        post,
        sender: User
    ):
        """Отправить уведомление о том, что пользователя процитировали"""
        # Не отправляем уведомление самому себе
        if quoted_user == sender:
            return None
            
        return NotificationService.create_notification(
            recipient=quoted_user,
            notification_type=NotificationType.FORUM_POST_QUOTED,
            title=f"Вас процитировали в теме '{topic.title}'",
            message=f"Пользователь {sender.get_full_name() or sender.username} процитировал ваше сообщение в теме '{topic.title}'",
            sender=sender,
            related_object_id=topic.id,
            related_object_type='forum_topic',
            extra_data={
                'topic_id': topic.id,
                'post_id': post.id,
                'topic_title': topic.title,
                'category_name': topic.category.name,
                'quoted_post_id': post.id
            }
        )
    
    @staticmethod
    def send_review_notification(
        recipient: User,
        review,
        notification_type: str,
        sender: Optional[User] = None
    ):
        """Отправить уведомление об отзыве"""
        if notification_type == NotificationType.REVIEW_LEFT:
            title = "Оставлен новый отзыв"
            message = f"Получен новый отзыв от {review.user.get_full_name()}"
        elif notification_type == NotificationType.REVIEW_APPROVED:
            title = "Отзыв одобрен"
            message = f"Ваш отзыв одобрен модератором"
        elif notification_type == NotificationType.REVIEW_DELETED:
            title = "Отзыв удален"
            message = f"Ваш отзыв был удален модератором"
        elif notification_type == NotificationType.REVIEW_RESPONSE:
            title = "Ответ на отзыв"
            message = f"Получен ответ на ваш отзыв"
        else:
            return
        
        return NotificationService.create_notification(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            sender=sender,
            related_object_id=review.id,
            related_object_type='review'
        )
    
    @staticmethod
    def send_blog_notification(
        recipient: User,
        blog_post,
        notification_type: str,
        sender: Optional[User] = None
    ):
        """Отправить уведомление о блоге"""
        if notification_type == NotificationType.BLOG_POST_PUBLISHED:
            title = "Новая статья в блоге"
            message = f"Опубликована новая статья '{blog_post.title}'"
        elif notification_type == NotificationType.BLOG_POST_APPROVED:
            title = "Статья одобрена"
            message = f"Ваша статья '{blog_post.title}' одобрена модератором"
        elif notification_type == NotificationType.BLOG_POST_REJECTED:
            title = "Статья отклонена"
            message = f"Ваша статья '{blog_post.title}' отклонена модератором"
        elif notification_type == NotificationType.BLOG_COMMENT:
            title = "Комментарий к статье"
            message = f"Новый комментарий к статье '{blog_post.title}'"
        else:
            return
        
        return NotificationService.create_notification(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            sender=sender,
            related_object_id=blog_post.id,
            related_object_type='blog_post'
        )
    
    @staticmethod
    def send_system_notification(
        recipients: List[User],
        notification_type: str,
        title: str,
        message: str,
        priority: str = NotificationPriority.NORMAL
    ):
        """Отправить системное уведомление"""
        notifications = []
        for recipient in recipients:
            notification = NotificationService.create_notification(
                recipient=recipient,
                notification_type=notification_type,
                title=title,
                message=message,
                priority=priority,
                related_object_type='system'
            )
            if notification:
                notifications.append(notification)
        return notifications
    
    @staticmethod
    def mark_as_read(notification_id: int, user: User) -> bool:
        """Отметить уведомление как прочитанное"""
        try:
            notification = Notification.objects.get(id=notification_id, recipient=user)
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            return False
    
    @staticmethod
    def mark_all_as_read(user: User) -> int:
        """Отметить все уведомления пользователя как прочитанные"""
        return Notification.objects.filter(recipient=user, is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
    
    @staticmethod
    def get_unread_count(user: User) -> int:
        """Получить количество непрочитанных уведомлений"""
        return Notification.objects.filter(recipient=user, is_read=False).count()
    
    @staticmethod
    def get_user_notifications(user: User, limit: int = 50) -> List[Notification]:
        """Получить уведомления пользователя"""
        return Notification.objects.filter(recipient=user).order_by('-created_at')[:limit]
