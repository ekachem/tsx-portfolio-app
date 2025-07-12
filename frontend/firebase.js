// firebase.js

// Import the Firebase modules you need (for CDN version, skip the import lines)
import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.0.0/firebase-app.js';
import { getAuth, GoogleAuthProvider, signInWithPopup, onAuthStateChanged } from 'https://www.gstatic.com/firebasejs/10.0.0/firebase-auth.js';
import { getFirestore } from 'https://www.gstatic.com/firebasejs/10.0.0/firebase-firestore.js';

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyCDd5rIxlkuSlXt_T3mJoCf_nkvrXufguA",
  authDomain: "tsx-portfolio-app.firebaseapp.com",
  projectId: "tsx-portfolio-app",
  storageBucket: "tsx-portfolio-app.firebasestorage.app",
  messagingSenderId: "1087400255017",
  appId: "1:1087400255017:web:2be393849fa1305be84638"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();
const db = getFirestore(app);

// Export to use in other scripts
export { app, auth, provider, db };

