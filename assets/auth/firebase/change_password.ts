import {auth} from './init';
import {signInWithEmailAndPassword, updatePassword, AuthError} from 'firebase/auth';

declare const firebaseUserEmail : string;

const form = document.getElementById('formChangePassword') as HTMLFormElement;
const firebaseStatus = document.getElementById('firebase-status') as HTMLInputElement;

if (form != null) {
    form.onsubmit = (event) => {
        event.preventDefault();

        const data = new FormData(form);
        const oldPassword = data.get('old_password') as string;
        const newPassword = data.get('new_password') as string;
        const newPassword2 = data.get('new_password2') as string;

        if (newPassword !== newPassword2) {
            form.submit();
        }

        signInWithEmailAndPassword(auth, firebaseUserEmail, oldPassword).then((userCredential) => {
            return updatePassword(userCredential.user, newPassword).then(() => {
                firebaseStatus.value = 'OK';
                form.submit();
            });
        }).catch((reason: AuthError) => {
            firebaseStatus.value = reason.code;
            form.submit();
        });

        return false;
    };
}

