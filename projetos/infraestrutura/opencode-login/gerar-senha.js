const crypto = require('crypto');

const password = process.argv[2];
if (!password) {
  console.log('Uso: node gerar-senha.js <senha>');
  process.exit(1);
}

const hash = crypto.createHash('sha256').update(password).digest('hex');
console.log(`Senha: ${password}`);
console.log(`Hash:   ${hash}`);
console.log(`\nAdicione no users.json:`);
console.log(`"passwordHash": "${hash}"`);
