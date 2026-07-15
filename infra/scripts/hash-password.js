#!/usr/bin/env node
// Gera hash bcrypt para senha.
// Uso: node hash-password.js <senha> [username]
//   node hash-password.js "v4@2025"
//   node hash-password.js "minhaSenha" marcos.luciano
const bcrypt = require('bcryptjs');
const pwd = process.argv[2] || 'v4@2025';
const username = process.argv[3] || 'usuario';
const hash = bcrypt.hashSync(pwd, 10);
console.log('Senha:', pwd);
console.log('Hash:', hash);
console.log('');
console.log(`UPDATE users SET password_hash = '${hash}' WHERE username = '${username}';`);
