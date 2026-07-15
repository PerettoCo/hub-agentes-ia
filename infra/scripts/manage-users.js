#!/usr/bin/env node
// CLI para gerenciar usuários do Hub de Agentes
// Uso:
//   node manage-users.js list                    — lista todos os usuários
//   node manage-users.js add <username> [opts]    — adiciona usuário
//   node manage-users.js remove <username>        — remove usuário
//   node manage-users.js passwd <username> <senha> — altera senha
//   node manage-users.js role <username> <role>   — altera função (user/admin)

const fs = require('fs');
const path = require('path');
const bcrypt = require('bcryptjs');

const USERS_PATH = process.env.USERS_PATH || '/data/users.json';
const DEFAULT_PASSWORD = process.env.DEFAULT_PASSWORD || 'v4@2025';

function loadUsers() {
  try {
    if (fs.existsSync(USERS_PATH)) {
      const raw = fs.readFileSync(USERS_PATH, 'utf-8');
      const data = JSON.parse(raw);
      if (Array.isArray(data)) return data;
      if (data.users && Array.isArray(data.users)) return data.users;
    }
  } catch (e) {
    console.error('Erro ao ler', USERS_PATH, e.message);
  }
  return [];
}

function saveUsers(users) {
  const dir = path.dirname(USERS_PATH);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(USERS_PATH, JSON.stringify({ users }, null, 2), 'utf-8');
  console.log(`Salvo ${users.length} usuários em ${USERS_PATH}`);
}

function list() {
  const users = loadUsers();
  if (users.length === 0) {
    console.log('Nenhum usuário encontrado.');
    return;
  }
  console.log('\nUsuários do Hub de Agentes:\n');
  users.forEach(u => {
    console.log(`  ${u.username.padEnd(20)} ${u.role.padEnd(6)} ${u.squad.padEnd(10)} ${u.name}`);
  });
  console.log(`\nTotal: ${users.length} usuários\n`);
}

function add(username, opts) {
  if (!username || username.length < 3) {
    console.error('Erro: username deve ter ao menos 3 caracteres');
    process.exit(1);
  }
  const users = loadUsers();
  if (users.some(u => u.username === username)) {
    console.error(`Erro: Usuário "${username}" já existe`);
    process.exit(1);
  }
  const password = opts.password || DEFAULT_PASSWORD;
  const user = {
    username,
    passwordHash: bcrypt.hashSync(password, 10),
    name: opts.name || username.split('.').map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(' '),
    email: opts.email || `${username}@fvmarketing.com.br`,
    squad: opts.squad || 'Geral',
    role: opts.role || 'user',
  };
  users.push(user);
  saveUsers(users);
  console.log(`Usuário "${username}" criado com sucesso.`);
  if (opts.password) console.log('Senha definida.');
  else console.log(`Senha padrão: ${DEFAULT_PASSWORD}`);
}

function remove(username) {
  const users = loadUsers();
  const idx = users.findIndex(u => u.username === username);
  if (idx < 0) {
    console.error(`Erro: Usuário "${username}" não encontrado`);
    process.exit(1);
  }
  const removed = users.splice(idx, 1);
  saveUsers(users);
  console.log(`Usuário "${removed[0].username}" removido.`);
}

function passwd(username, password) {
  if (!password || password.length < 4) {
    console.error('Erro: Senha deve ter ao menos 4 caracteres');
    process.exit(1);
  }
  const users = loadUsers();
  const user = users.find(u => u.username === username);
  if (!user) {
    console.error(`Erro: Usuário "${username}" não encontrado`);
    process.exit(1);
  }
  user.passwordHash = bcrypt.hashSync(password, 10);
  saveUsers(users);
  console.log(`Senha do usuário "${username}" alterada.`);
}

function setRole(username, role) {
  if (!['admin', 'user'].includes(role)) {
    console.error('Erro: Role deve ser "admin" ou "user"');
    process.exit(1);
  }
  const users = loadUsers();
  const user = users.find(u => u.username === username);
  if (!user) {
    console.error(`Erro: Usuário "${username}" não encontrado`);
    process.exit(1);
  }
  user.role = role;
  saveUsers(users);
  console.log(`Role de "${username}" alterada para "${role}".`);
}

const cmd = process.argv[2];
const args = process.argv.slice(3);

switch (cmd) {
  case 'list':
    list();
    break;
  case 'add': {
    const username = args[0];
    const opts = {};
    for (let i = 1; i < args.length; i++) {
      if (args[i] === '--name' && args[i+1]) opts.name = args[++i];
      else if (args[i] === '--email' && args[i+1]) opts.email = args[++i];
      else if (args[i] === '--squad' && args[i+1]) opts.squad = args[++i];
      else if (args[i] === '--role' && args[i+1]) opts.role = args[++i];
      else if (args[i] === '--password' && args[i+1]) opts.password = args[++i];
    }
    add(username, opts);
    break;
  }
  case 'remove':
    remove(args[0]);
    break;
  case 'passwd':
    passwd(args[0], args[1]);
    break;
  case 'role':
    setRole(args[0], args[1]);
    break;
  default:
    console.log(`
Uso: node manage-users.js <comando> [args]

Comandos:
  list                                    Listar usuários
  add <username> [opts]                   Adicionar usuário
  remove <username>                       Remover usuário
  passwd <username> <senha>               Alterar senha
  role <username> <admin|user>            Alterar função

Opções para "add":
  --name "Nome Completo"     Nome do usuário
  --email email@exemplo.com  Email
  --squad "Growth"           Squad
  --role admin               user (padrão) ou admin
  --password "senha"         Senha (padrão: v4@2025)

Exemplos:
  node manage-users.js add maria.silva --name "Maria Silva" --role admin
  node manage-users.js passwd marcos.luciano "novaSenha123"
  node manage-users.js list
`);
}
