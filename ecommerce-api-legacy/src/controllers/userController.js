const userModel = require('../models/userModel');

async function deleteUser(id) {
  await userModel.remove(id);
  return { data: { msg: 'Usuário deletado com sucesso' }, status: 200 };
}

module.exports = { deleteUser };
