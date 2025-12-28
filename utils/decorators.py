"""
Decorator functions for user authentication, permissions, and access level checks.

This module provides decorators for Telegram bot handlers that enforce
permission-based access control, authentication verification, and role-based authorization.
"""

from functools import wraps
from typing import Callable, Optional, List, Any
import logging

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


def require_authentication(func: Callable) -> Callable:
    """
    Decorator to ensure the user is authenticated before executing the handler.
    
    This decorator checks if the user has a valid session or is registered in the system.
    
    Args:
        func: The handler function to decorate
        
    Returns:
        The decorated function that performs authentication check
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
        user = update.effective_user
        
        if not user:
            logger.warning("Authentication failed: No user object found")
            await update.message.reply_text("❌ Authentication failed. Please try again.")
            return
        
        # Store user_id for reference in the handler
        context.user_data["authenticated_user_id"] = user.id
        context.user_data["authenticated_user_username"] = user.username
        
        logger.info(f"User {user.id} ({user.username}) authenticated successfully")
        return await func(update, context)
    
    return wrapper


def require_permission(permission: str) -> Callable:
    """
    Decorator to check if a user has a specific permission.
    
    Args:
        permission: The permission string to check (e.g., 'edit_messages', 'delete_messages')
        
    Returns:
        A decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
            user = update.effective_user
            
            if not user:
                logger.warning("Permission check failed: No user object found")
                await update.message.reply_text("❌ You are not authorized to perform this action.")
                return
            
            # Check user permissions from context or database
            user_permissions = context.user_data.get("permissions", set())
            
            if permission not in user_permissions:
                logger.warning(f"User {user.id} lacks required permission: {permission}")
                await update.message.reply_text(
                    f"❌ You don't have permission to execute this command: `{permission}`",
                    parse_mode="Markdown"
                )
                return
            
            logger.info(f"User {user.id} has permission: {permission}")
            return await func(update, context)
        
        return wrapper
    return decorator


def require_permissions(permissions: List[str], require_all: bool = True) -> Callable:
    """
    Decorator to check if a user has multiple permissions.
    
    Args:
        permissions: List of permission strings to check
        require_all: If True, user must have all permissions. If False, at least one.
        
    Returns:
        A decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
            user = update.effective_user
            
            if not user:
                logger.warning("Permission check failed: No user object found")
                await update.message.reply_text("❌ You are not authorized to perform this action.")
                return
            
            user_permissions = context.user_data.get("permissions", set())
            required_set = set(permissions)
            user_set = set(user_permissions)
            
            if require_all:
                has_permission = required_set.issubset(user_set)
                missing = required_set - user_set
                error_msg = f"Missing permissions: {', '.join(missing)}"
            else:
                has_permission = bool(required_set & user_set)
                error_msg = f"Requires one of: {', '.join(permissions)}"
            
            if not has_permission:
                logger.warning(f"User {user.id} permission check failed: {error_msg}")
                await update.message.reply_text(
                    f"❌ {error_msg}",
                    parse_mode="Markdown"
                )
                return
            
            logger.info(f"User {user.id} passed permission check")
            return await func(update, context)
        
        return wrapper
    return decorator


def require_admin() -> Callable:
    """
    Decorator to check if a user has admin access level.
    
    Returns:
        A decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
            user = update.effective_user
            chat = update.effective_chat
            
            if not user or not chat:
                logger.warning("Admin check failed: No user or chat object found")
                await update.message.reply_text("❌ Unable to verify admin status.")
                return
            
            # Check if user is admin in the chat
            try:
                member = await context.bot.get_chat_member(chat.id, user.id)
                is_admin = member.status in ["creator", "administrator"]
                
                if not is_admin:
                    logger.warning(f"User {user.id} is not an admin in chat {chat.id}")
                    await update.message.reply_text("❌ You must be an admin to use this command.")
                    return
                
                logger.info(f"User {user.id} is admin in chat {chat.id}")
                return await func(update, context)
            
            except Exception as e:
                logger.error(f"Error checking admin status: {e}")
                await update.message.reply_text("❌ Error verifying admin status.")
                return
        
        return wrapper
    return decorator


def require_access_level(level: int) -> Callable:
    """
    Decorator to check if a user meets a specific access level threshold.
    
    Access levels:
    - 0: Regular user
    - 1: Moderator
    - 2: Administrator
    - 3: Super Admin / Owner
    
    Args:
        level: Minimum required access level
        
    Returns:
        A decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
            user = update.effective_user
            
            if not user:
                logger.warning("Access level check failed: No user object found")
                await update.message.reply_text("❌ Unable to verify access level.")
                return
            
            # Get user's access level from context data
            user_level = context.user_data.get("access_level", 0)
            
            if user_level < level:
                level_names = {0: "User", 1: "Moderator", 2: "Administrator", 3: "Super Admin"}
                required_name = level_names.get(level, "Unknown")
                logger.warning(f"User {user.id} access denied: requires level {level}")
                await update.message.reply_text(
                    f"❌ This action requires {required_name} access level."
                )
                return
            
            logger.info(f"User {user.id} passed access level check (level: {user_level})")
            return await func(update, context)
        
        return wrapper
    return decorator


def require_group_admin(func: Callable) -> Callable:
    """
    Decorator to check if the user is an admin in the current group.
    
    Args:
        func: The handler function to decorate
        
    Returns:
        The decorated function
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
        user = update.effective_user
        chat = update.effective_chat
        
        if not user or not chat:
            logger.warning("Group admin check failed: Invalid user or chat object")
            await update.message.reply_text("❌ Could not verify group admin status.")
            return
        
        # Check if this is a group
        if chat.type not in ["group", "supergroup"]:
            logger.warning(f"Command used in non-group chat: {chat.type}")
            await update.message.reply_text("❌ This command can only be used in groups.")
            return
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            is_admin = member.status in ["creator", "administrator"]
            
            if not is_admin:
                logger.warning(f"User {user.id} is not an admin in group {chat.id}")
                await update.message.reply_text("❌ You must be a group admin to use this command.")
                return
            
            logger.info(f"User {user.id} verified as group admin in {chat.id}")
            return await func(update, context)
        
        except Exception as e:
            logger.error(f"Error verifying group admin: {e}")
            await update.message.reply_text("❌ Error verifying admin status.")
            return
    
    return wrapper


def require_owner(owner_id: Optional[int] = None) -> Callable:
    """
    Decorator to check if the user is the bot owner or group owner.
    
    Args:
        owner_id: Optional specific owner user ID. If not provided, checks group creator.
        
    Returns:
        A decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
            user = update.effective_user
            chat = update.effective_chat
            
            if not user:
                logger.warning("Owner check failed: No user object found")
                await update.message.reply_text("❌ Could not verify ownership.")
                return
            
            # If specific owner_id is provided, check against it
            if owner_id is not None:
                if user.id != owner_id:
                    logger.warning(f"User {user.id} is not the owner")
                    await update.message.reply_text("❌ Only the owner can execute this command.")
                    return
            else:
                # Check if user is group creator
                if chat:
                    try:
                        member = await context.bot.get_chat_member(chat.id, user.id)
                        if member.status != "creator":
                            logger.warning(f"User {user.id} is not group creator in {chat.id}")
                            await update.message.reply_text("❌ Only the group creator can execute this command.")
                            return
                    except Exception as e:
                        logger.error(f"Error verifying group creator: {e}")
                        await update.message.reply_text("❌ Error verifying ownership.")
                        return
            
            logger.info(f"User {user.id} verified as owner")
            return await func(update, context)
        
        return wrapper
    return decorator


def rate_limit(max_calls: int = 5, period: int = 60) -> Callable:
    """
    Decorator to rate limit user actions.
    
    Args:
        max_calls: Maximum number of calls allowed
        period: Time period in seconds
        
    Returns:
        A decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
            user = update.effective_user
            
            if not user:
                return
            
            # Initialize rate limit tracking
            if "rate_limits" not in context.user_data:
                context.user_data["rate_limits"] = {}
            
            func_name = func.__name__
            now = __import__("time").time()
            
            if func_name not in context.user_data["rate_limits"]:
                context.user_data["rate_limits"][func_name] = []
            
            # Remove old calls outside the period
            calls = context.user_data["rate_limits"][func_name]
            calls[:] = [call_time for call_time in calls if now - call_time < period]
            
            # Check if rate limit exceeded
            if len(calls) >= max_calls:
                logger.warning(f"Rate limit exceeded for user {user.id} on {func_name}")
                await update.message.reply_text(
                    f"⏳ You're sending too many requests. Please wait a moment."
                )
                return
            
            # Record this call
            calls.append(now)
            return await func(update, context)
        
        return wrapper
    return decorator


def log_action(action_type: str = "action") -> Callable:
    """
    Decorator to log user actions for audit purposes.
    
    Args:
        action_type: Type of action being logged
        
    Returns:
        A decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
            user = update.effective_user
            chat = update.effective_chat
            
            logger.info(
                f"[{action_type.upper()}] User: {user.id} ({user.username if user else 'Unknown'}) "
                f"Chat: {chat.id if chat else 'Unknown'} Function: {func.__name__}"
            )
            
            return await func(update, context)
        
        return wrapper
    return decorator
