require('dotenv').config();
const express = require('express');
const { initDb } = require('./config/database');
const checkoutRoutes = require('./routes/checkoutRoutes');
const reportRoutes = require('./routes/reportRoutes');
const userRoutes = require('./routes/userRoutes');

const app = express();
app.use(express.json());

app.use('/api/checkout', checkoutRoutes);
app.use('/api/admin', reportRoutes);
app.use('/api/users', userRoutes);

const PORT = process.env.PORT || 3000;

initDb().then(() => {
  app.listen(PORT, () => {
    console.log(`LMS API rodando na porta ${PORT}`);
  });
}).catch(err => {
  console.error('Erro ao inicializar banco de dados:', err);
  process.exit(1);
});
