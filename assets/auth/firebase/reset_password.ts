import {auth} from './init';
import {sendPasswordResetEmail} from 'firebase/auth';
import {reportFirebaseAuthError} from './sentry';

declare const nextUrl: string;

const form = document.getElementById('formToken') as HTMLFormElement;
const url = new URL(nextUrl);
const params = new URLSearchParams(url.search);
const sendButton = document.getElementById('reset-password-btn') as HTMLButtonElement;

if (sendButton != null) {
    form.onsubmit = (event) => {
        event.preventDefault();

        if (sendButton.disabled) {
            return false;
        }

        const data = new FormData(form);
        const email = data.get('email') as string;

        params.append('email', email);
        url.search = params.toString();

        debugger;

        sendButton.disabled = true;
        sendPasswordResetEmail(auth, email, {url: url.toString()})
            .then(() => {
                form.submit();
            })
            .catch((reason) => {
                reportFirebaseAuthError(reason, {
                    action: 'reset_password',
                    email,
                    extra: {
                        nextPath: url.pathname,
                    },
                });

                if (reason.code === 'auth/user-not-found') {
                    // User not registered with OAuth, try attempting normal password reset
                    form.submit();
                } else {
                    console.error(reason);
                    sendButton.disabled = false; // allow another request if there was an error
                }
            });

        return false;
    };
}