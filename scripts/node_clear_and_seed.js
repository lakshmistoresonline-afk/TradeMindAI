const fs = require('fs');
const crypto = require('crypto');
const path = require('path');

const serviceAccountPath = path.join(__dirname, '../backend/service-account.json');
const serviceAccount = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));

function base64UrlEncode(str) {
  return Buffer.from(str)
    .toString('base64')
    .replace(/=/g, '')
    .replace(/\+/g, '-')
    .replace(/\//g, '_');
}

async function getAccessToken() {
  const header = { alg: 'RS256', typ: 'JWT' };
  const now = Math.floor(Date.now() / 1000);
  const claimSet = {
    iss: serviceAccount.client_email,
    scope: 'https://www.googleapis.com/auth/datastore https://www.googleapis.com/auth/cloud-platform',
    aud: serviceAccount.token_uri,
    exp: now + 3600,
    iat: now
  };

  const encodedHeader = base64UrlEncode(JSON.stringify(header));
  const encodedClaimSet = base64UrlEncode(JSON.stringify(claimSet));
  const signatureInput = `${encodedHeader}.${encodedClaimSet}`;

  const signer = crypto.createSign('RSA-SHA256');
  signer.update(signatureInput);
  const signature = signer.sign(serviceAccount.private_key, 'base64')
    .replace(/=/g, '')
    .replace(/\+/g, '-')
    .replace(/\//g, '_');

  const jwt = `${signatureInput}.${signature}`;

  const res = await fetch(serviceAccount.token_uri, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer',
      assertion: jwt
    })
  });

  const tokenData = await res.json();
  return tokenData.access_token;
}

async function clearCollection(token, collectionName) {
  const projectId = serviceAccount.project_id;
  const listUrl = `https://firestore.googleapis.com/v1/projects/${projectId}/databases/(default)/documents/${collectionName}?pageSize=300`;

  const res = await fetch(listUrl, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await res.json();

  if (!data.documents) return;

  console.log(`Deleting ${data.documents.length} old documents from ${collectionName}...`);
  for (const doc of data.documents) {
    await fetch(`https://firestore.googleapis.com/v1/${doc.name}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    });
  }
}

async function run() {
  console.log("Purging old database records to fix mobile layout issues with stale legacy signals...");
  const token = await getAccessToken();
  await clearCollection(token, 'signals');
  await clearCollection(token, 'signals_history');
  console.log("Database purged successfully. You can now run node_update_all_data.js to seed fresh V5.0 records.");
}

run();
