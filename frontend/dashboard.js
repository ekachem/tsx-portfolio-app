import { auth, provider, db } from './firebase.js';
import {
  signInWithPopup,
  signOut,
  onAuthStateChanged
} from 'https://www.gstatic.com/firebasejs/10.0.0/firebase-auth.js';
import {
  collection,
  getDocs,
  addDoc
} from 'https://www.gstatic.com/firebasejs/10.0.0/firebase-firestore.js';

const loginButton = document.getElementById('loginButton');
const logoutButton = document.getElementById('logoutButton');
const userInfo = document.getElementById('userInfo');
const portfolioSection = document.getElementById('portfolioSection');
const portfolioList = document.getElementById('portfolioList');
const analyzeButton = document.getElementById('analyzeButton');
const analysisResult = document.getElementById('analysisResult');
const tickerInput = document.getElementById('tickerInput');
const sharesInput = document.getElementById('sharesInput');
const buyPriceInput = document.getElementById('buyPriceInput');
const addStockButton = document.getElementById('addStockButton');

loginButton.addEventListener('click', () => {
  signInWithPopup(auth, provider)
    .then(result => console.log('Logged in:', result.user.uid))
    .catch(error => console.error('Login error:', error));
});

logoutButton.addEventListener('click', () => {
  signOut(auth)
    .then(() => console.log('Logged out'))
    .catch(error => console.error('Logout error:', error));
});

onAuthStateChanged(auth, async (user) => {
  if (user) {
    userInfo.textContent = `Logged in as ${user.email}`;
    loginButton.style.display = 'none';
    logoutButton.style.display = 'inline';
    portfolioSection.style.display = 'block';

    await loadPortfolio(user.uid);

    addStockButton.addEventListener('click', async () => {
      const ticker = tickerInput.value.trim();
      const shares = Number(sharesInput.value);
      const buyPrice = Number(buyPriceInput.value);

      if (!ticker || shares <= 0 || buyPrice <= 0) {
        alert('Please enter valid ticker, shares, and buy price.');
        return;
      }

      await addDoc(collection(db, 'users', user.uid, 'portfolio'), {
        ticker: ticker.toUpperCase(),
        shares,
        buy_price: buyPrice,
        date: new Date().toISOString().split('T')[0]
      });

      alert('Stock added! Please reload to see updates.');
      tickerInput.value = '';
      sharesInput.value = '';
      buyPriceInput.value = '';
    });

    analyzeButton.addEventListener('click', async () => {
      analysisResult.textContent = 'Running analysis...';

      const portfolioSnapshot = await getDocs(collection(db, 'users', user.uid, 'portfolio'));
      const portfolioArray = [];
      portfolioSnapshot.forEach(doc => {
        const data = doc.data();
        portfolioArray.push({
          ticker: data.ticker,
          shares: data.shares,
          buy_price: data.buy_price,
          date: data.date
        });
      });

      try {
        const response = await fetch('https://tsx-portfolio-app.onrender.com/api/analyze-portfolio', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(portfolioArray)
        });

        if (!response.ok) {
          throw new Error('Backend error');
        }

        const result = await response.json();
        analysisResult.textContent = `Current value: $${result.latest_value}, Growth: ${result.growth.toFixed(2)}%`;
      } catch (error) {
        analysisResult.textContent = 'Error running analysis.';
        console.error(error);
      }
    });

  } else {
    userInfo.textContent = 'Not logged in';
    loginButton.style.display = 'inline';
    logoutButton.style.display = 'none';
    portfolioSection.style.display = 'none';
  }
});

async function loadPortfolio(uid) {
  const portfolioSnapshot = await getDocs(collection(db, 'users', uid, 'portfolio'));
  portfolioList.innerHTML = '';
  portfolioSnapshot.forEach(doc => {
    const data = doc.data();
    portfolioList.innerHTML += `<li>${data.ticker}: ${data.shares} shares @ $${data.buy_price}</li>`;
  });
}

