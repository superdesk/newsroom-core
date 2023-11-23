import {getAuth} from 'firebase/auth';
import {initializeApp} from 'firebase/app';

declare const firebaseConfig : {
    apiKey: string;
    authDomain: string;
    projectId: string;
    messagingSenderId: string;
};

export const app = initializeApp(firebaseConfig);
export const auth = getAuth();
