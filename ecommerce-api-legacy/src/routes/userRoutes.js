const express = require('express');
const router = express.Router();
const userController = require('../controllers/userController');

router.delete('/:id', async (req, res) => {
  try {
    const result = await userController.deleteUser(req.params.id);
    return res.status(result.status).json(result.data);
  } catch (err) {
    return res.status(500).json({ error: 'Erro interno do servidor' });
  }
});

module.exports = router;
