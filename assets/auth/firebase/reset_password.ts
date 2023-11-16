import {auth} from './init';
import {sendPasswordResetEmail} from 'firebase/auth';

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

        sendButton.disabled = true;
        sendPasswordResetEmail(auth, email, {url: url.toString()})
            .then(() => {
                // set `email_sent` to true, so server knows password reset was handled by firebase
                form.submit();
            })
            .catch((reason) => {
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