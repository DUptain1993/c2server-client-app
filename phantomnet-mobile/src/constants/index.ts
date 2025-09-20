// Constants for PhantomNet C2 Mobile App

export const COLORS = {
  // Primary Colors
  primary: '#667eea',
  primaryDark: '#5a6fd8',
  primaryLight: '#8394f4',

  // Secondary Colors
  secondary: '#764ba2',
  secondaryDark: '#6a4190',
  secondaryLight: '#9675b4',

  // Accent Colors
  accent: '#f093fb',
  accentDark: '#e683f7',
  accentLight: '#f4a3fc',

  // Neutral Colors
  background: '#f8f9fa',
  surface: '#ffffff',
  surfaceVariant: '#f1f3f4',

  // Text Colors
  text: '#212121',
  textSecondary: '#757575',
  textMuted: '#9e9e9e',

  // Status Colors
  success: '#4caf50',
  successLight: '#81c784',
  error: '#f44336',
  errorLight: '#ef5350',
  warning: '#ff9800',
  warningLight: '#ffb74d',
  info: '#2196f3',
  infoLight: '#64b5f6',

  // Border Colors
  border: '#e0e0e0',
  borderLight: '#f0f0f0',
} as const;

export const FONTS = {
  regular: 'System',
  medium: 'System',
  bold: 'System',
  light: 'System',
} as const;

export const FONT_SIZES = {
  xs: 12,
  sm: 14,
  md: 16,
  lg: 18,
  xl: 20,
  xxl: 24,
  xxxl: 32,
} as const;

export const SPACING = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
} as const;

export const BORDER_RADIUS = {
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  xxl: 24,
  round: 50,
} as const;

export const SHADOWS = {
  sm: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.22,
    shadowRadius: 2.22,
    elevation: 3,
  },
  md: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  lg: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.30,
    shadowRadius: 4.65,
    elevation: 8,
  },
} as const;

export const API_ENDPOINTS = {
  // Authentication
  LOGIN: '/admin/login',
  LOGOUT: '/admin/logout',

  // Dashboard
  DASHBOARD: '/admin/dashboard',

  // Bots
  BOTS: '/admin/bots',
  BOT_COMMANDS: (botId: string) => `/bot/command/${botId}`,

  // Commands
  SEND_COMMAND: '/admin/commands',

  // Payloads
  PAYLOADS: '/admin/payloads',
  GENERATE_PAYLOAD: '/admin/payloads',
  DOWNLOAD_PAYLOAD: (payloadId: number) => `/admin/payloads/${payloadId}/download`,

  // Targets
  TARGETS: '/admin/targets',
  DISCOVER_TARGETS: '/admin/targets/discover',

  // Campaigns
  CAMPAIGNS: '/admin/campaigns',
  CREATE_CAMPAIGN: '/admin/campaigns',

  // Exploits
  EXPLOITS: '/admin/exploits',

  // Tasks
  TASKS: '/admin/tasks',

  // Statistics
  STATS: '/admin/stats',

  // DuckDNS
  DUCKDNS_UPDATE: '/admin/duckdns/update',
  DUCKDNS_TOGGLE: '/admin/duckdns/toggle',
} as const;

export const SERVER_CONFIG = {
  DEFAULT_URL: 'https://phantomnet-c2-22335118220.us-central1.run.app',
  DEFAULT_PORT: 443, // Cloud Run uses standard HTTPS port
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 second
} as const;

export const STORAGE_KEYS = {
  SERVER_CONFIG: 'server_config',
  AUTH_TOKEN: 'auth_token',
  USER_DATA: 'user_data',
  THEME: 'theme',
  LAST_SYNC: 'last_sync',
  OFFLINE_DATA: 'offline_data',
} as const;

export const BOT_STATUSES = {
  ACTIVE: 'active',
  INACTIVE: 'inactive',
  OFFLINE: 'offline',
} as const;

export const COMMAND_STATUSES = {
  PENDING: 'pending',
  RUNNING: 'running',
  COMPLETED: 'completed',
  FAILED: 'failed',
} as const;

export const CAMPAIGN_STATUSES = {
  ACTIVE: 'active',
  PAUSED: 'paused',
  COMPLETED: 'completed',
} as const;

export const PAYLOAD_TYPES = {
  WINDOWS: {
    EXE: 'exe',
    DLL: 'dll',
  },
  LINUX: {
    ELF: 'elf',
    SH: 'sh',
  },
  MACOS: {
    MACHO: 'macho',
  },
} as const;

export const PLATFORMS = {
  WINDOWS: 'windows',
  LINUX: 'linux',
  MACOS: 'macos',
} as const;

export const ARCHITECTURES = {
  X86: 'x86',
  X64: 'x64',
} as const;

export const EXPLOIT_TYPES = {
  RCE: 'rce',
  LFI: 'lfi',
  SQLI: 'sqli',
  XSS: 'xss',
  CSRF: 'csrf',
} as const;

export const TASK_TYPES = {
  EXECUTE: 'execute',
  DOWNLOAD: 'download',
  UPLOAD: 'upload',
  SCAN: 'scan',
  KEYLOGGER: 'keylogger',
  SCREENSHOT: 'screenshot',
  SYSTEM_INFO: 'system_info',
} as const;

export const REFRESH_INTERVALS = {
  DASHBOARD: 30000, // 30 seconds
  BOTS: 15000, // 15 seconds
  COMMANDS: 10000, // 10 seconds
  TARGETS: 60000, // 1 minute
  CAMPAIGNS: 30000, // 30 seconds
} as const;

export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
} as const;

export const VALIDATION_RULES = {
  USERNAME: {
    MIN_LENGTH: 3,
    MAX_LENGTH: 50,
    PATTERN: /^[a-zA-Z0-9_-]+$/,
  },
  PASSWORD: {
    MIN_LENGTH: 8,
    MAX_LENGTH: 128,
    REQUIRE_UPPERCASE: true,
    REQUIRE_LOWERCASE: true,
    REQUIRE_NUMBERS: true,
    REQUIRE_SPECIAL_CHARS: false,
  },
  SERVER_URL: {
    PATTERN: /^https?:\/\/[^\s/$.?#].[^\s]*$/,
  },
  BOT_ID: {
    PATTERN: /^[a-zA-Z0-9_-]+$/,
    MAX_LENGTH: 50,
  },
  PAYLOAD_NAME: {
    MIN_LENGTH: 1,
    MAX_LENGTH: 100,
    PATTERN: /^[a-zA-Z0-9_-]+$/,
  },
} as const;

export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network connection failed. Please check your internet connection.',
  SERVER_ERROR: 'Server error occurred. Please try again later.',
  AUTH_ERROR: 'Authentication failed. Please check your credentials.',
  TIMEOUT_ERROR: 'Request timed out. Please try again.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  UNKNOWN_ERROR: 'An unexpected error occurred. Please try again.',
} as const;

export const SUCCESS_MESSAGES = {
  LOGIN_SUCCESS: 'Successfully logged in!',
  COMMAND_SENT: 'Command sent successfully!',
  PAYLOAD_GENERATED: 'Payload generated successfully!',
  TARGET_DISCOVERED: 'Target discovery completed!',
  CAMPAIGN_CREATED: 'Campaign created successfully!',
  SETTINGS_UPDATED: 'Settings updated successfully!',
} as const;

export const ANIMATION_DURATIONS = {
  FAST: 200,
  NORMAL: 300,
  SLOW: 500,
} as const;

export const SCREEN_NAMES = {
  LOGIN: 'Login',
  DASHBOARD: 'Dashboard',
  BOTS: 'Bots',
  BOT_DETAILS: 'BotDetails',
  COMMANDS: 'Commands',
  PAYLOADS: 'Payloads',
  TARGETS: 'Targets',
  CAMPAIGNS: 'Campaigns',
  SETTINGS: 'Settings',
  DATABASE: 'Database',
} as const;
