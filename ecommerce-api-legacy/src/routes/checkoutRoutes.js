const express = require('express');
const router = express.Router();
const checkoutController = require('../controllers/checkoutController');

router.post('/', async (req, res) => {
  try {
    const result = await checkoutController.checkout(req.body);
    if (result.error) return res.status(result.status).json({ error: result.error });
    return res.status(result.status).json(result.data);
  } catch (err) {
    return res.status(500).json({ error: 'Erro interno do servidor' });
  }
});

module.exports = router;
