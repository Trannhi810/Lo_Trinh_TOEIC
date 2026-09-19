// ===================================================
// FIREBASE FIRESTORE SYNC CONFIGURATION
// TOEIC Roadmap Multi-Device Real-time Synchronization
// ===================================================

const firebaseConfig = {
  apiKey: "AIzaSyABBnkPQMWV98BdUnJMEpHMLePSNshFxuU",
  authDomain: "toeic-roadmap.firebaseapp.com",
  projectId: "toeic-roadmap",
  storageBucket: "toeic-roadmap.firebasestorage.app",
  messagingSenderId: "605605075238",
  appId: "1:605605075238:web:84eed543fb6edd41d5c9e7",
  measurementId: "G-9BG17L6TB1"
};

// Initialize Firebase
if (typeof firebase !== 'undefined' && !firebase.apps.length) {
  firebase.initializeApp(firebaseConfig);
}

const db = (typeof firebase !== 'undefined') ? firebase.firestore() : null;
const docRef = db ? db.collection('toeic_app').doc('shared_data') : null;

window.FirebaseSync = {
  db,
  docRef,
  
  // Save specific field data to Firestore
  saveData: function(field, data) {
    if (!docRef) return;
    const updateObj = {};
    updateObj[field] = data;
    updateObj['updatedAt'] = firebase.firestore.FieldValue.serverTimestamp();
    
    docRef.set(updateObj, { merge: true }).catch(err => {
      console.warn("Firebase sync error:", err);
    });
  },
  
  // Listen for real-time changes
  onSync: function(callback) {
    if (!docRef) return () => {};
    return docRef.onSnapshot(doc => {
      if (doc.exists) {
        callback(doc.data());
      }
    }, err => {
      console.warn("Firebase snapshot listener error:", err);
    });
  }
};
