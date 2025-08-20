# Overview

This is a comprehensive Telegram bot that serves as a file management system with AI assistance and URL shortening capabilities. The bot allows users to upload files up to 5GB, store them in Telegram channels for fast access, integrate with Google Drive for private storage, shorten URLs using GPLinks, and interact with an AI assistant powered by Gemini AI. It supports all major file formats including documents, images, videos, audio files, archives, and applications.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Bot Framework
- **Technology**: Python-telegram-bot library for Telegram API integration
- **Architecture Pattern**: Command-handler pattern with separate modules for different functionalities
- **Message Handling**: Event-driven architecture using handlers for different file types (documents, photos, videos, audio)

## File Storage Strategy
- **Primary Storage**: Telegram channels as storage backend for files up to 5GB
- **Metadata Storage**: SQLite database for file metadata, download tracking, and URL shortening records
- **File Identification**: Custom file ID generation using timestamp and random alphanumeric characters
- **File Type Support**: Comprehensive support for documents, images, videos, audio, archives, and applications

## Database Design
- **Technology**: SQLite with aiosqlite for async operations
- **Schema**: Two main tables - `files` for file metadata and `shortened_urls` for URL shortening records
- **Features**: Tracks file metadata, download counts, Google Drive links, privacy settings, and deletion status

## AI Integration
- **Service**: Google Gemini AI (gemini-2.5-flash model)
- **Purpose**: File analysis assistance and general chat capabilities
- **Implementation**: Context-aware responses with optional file context integration

## External Service Integrations
- **Google Drive**: OAuth2-based integration for private file storage with service account support
- **GPLinks**: URL shortening service with API key authentication
- **Telegram Storage**: Uses designated Telegram channels as file storage backend

## Configuration Management
- **Environment Variables**: Centralized configuration using python-dotenv
- **Security**: API keys and sensitive data managed through environment variables
- **File Limits**: Configurable file size limits and allowed file types

## Error Handling and Logging
- **Logging**: Structured logging with timestamp, module name, and severity levels
- **Validation**: File size validation, file type checking, and URL format validation
- **Graceful Degradation**: Services continue operating even if optional integrations are unavailable

# External Dependencies

## Required Services
- **Telegram Bot API**: Core messaging and file handling platform
- **SQLite Database**: Local file metadata storage
- **Python Libraries**: python-telegram-bot, aiosqlite, python-dotenv

## Optional Integrations
- **Google Gemini AI**: AI assistant functionality (requires GEMINI_API_KEY)
- **Google Drive API**: Private file storage (requires GOOGLE_DRIVE_CLIENT_ID and GOOGLE_DRIVE_CLIENT_SECRET)
- **GPLinks API**: URL shortening service (requires GPLINKS_API_KEY)

## Environment Configuration
- **BOT_TOKEN**: Telegram bot authentication token (required)
- **STORAGE_CHANNEL_ID**: Telegram channel for file storage
- **GEMINI_API_KEY**: Google AI service authentication
- **GOOGLE_DRIVE_CLIENT_ID/SECRET**: OAuth2 credentials for Drive integration
- **GPLINKS_API_KEY**: URL shortening service authentication

## File System Dependencies
- **Storage Directory**: Local `storage/` directory for SQLite database
- **File Size Limits**: 5GB maximum file size support
- **File Type Validation**: Configurable allowed file extensions list