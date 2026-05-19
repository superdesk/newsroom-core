type SentryContext = {
    tags?: Record<string, string>;
    extra?: Record<string, unknown>;
};

type ReportAuthErrorOptions = {
    action: 'change_password' | 'login' | 'reset_password';
    email?: string;
    ignoredCodes?: string[];
    extra?: Record<string, unknown>;
};

function getEmailTelemetry(email: string): Record<string, string> {
    const [localPart = '', domain = ''] = email.trim().toLowerCase().split('@');
    const maskedLocalPart = localPart.length <= 2 ? `${localPart.charAt(0)}*` :
        `${localPart.slice(0, 2)}***${localPart.slice(-1)}`;

    return {
        emailDomain: domain,
        emailHint: domain ? `${maskedLocalPart}@${domain}` : maskedLocalPart,
    };
}

export function reportFirebaseAuthError(reason: unknown, options: ReportAuthErrorOptions): void {
    const code = typeof reason === 'object' && reason != null && 'code' in reason ? String(reason.code) : undefined;

    if (code != null && options.ignoredCodes?.includes(code)) {
        return;
    }

    const context: SentryContext = {
        tags: {
            area: 'auth',
            provider: 'firebase',
            action: options.action,
        },
        extra: {
            code,
            page: window.location.pathname,
            ...(options.email ? getEmailTelemetry(options.email) : {}),
            ...options.extra,
        },
    };

    try {
        window.Sentry?.captureException(reason, context);
    } catch {
        // Never let optional telemetry break the auth flow.
    }
}