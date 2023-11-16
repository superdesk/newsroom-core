import {auth} from './init';
import {signInWithEmailAndPassword, signOut} from 'firebase/auth';

const form = document.getElementById('formLogin') as HTMLFormElement;
const params = new URLSearchParams(window.location.search);

if (params.get('email')) {
    form['email'].value = params.get('email');
}

const sendTokenToServer = (token: string) => {
    window.location.replace(`/firebase_auth_token?token=${token}`);
};

// check firebase auth status
auth.onAuthStateChanged((user) => {
    if (user != null) { // there is a firebase user authenticated
        if (params.get('user_error') === '1') { // but missing in newshub
            return;
        }

        if (params.get('logout') === '1') { // force logout from firebase
            signOut(auth);
            return;
        }

        const tokenError = params.get('token_error');

        user.getIdToken(tokenError === '1').then(sendTokenToServer);
    }
});

// override submit form action to authenticate using firebase
// and fallback to newshub when credentials are invalid
form.onsubmit = (event) => {
    event.preventDefault();

    const data = new FormData(form);
    const email = data.get('email') as string;
    const password = data.get('password') as string;

    signInWithEmailAndPassword(auth, email, password).then((userCredential) => {
        userCredential.user.getIdToken().then(sendTokenToServer);
    }, (reason) => {
        // login via firebase didn't work out,
        // try standard newshub login
        console.error(reason);
        form.submit();
    });

    return false;
};
