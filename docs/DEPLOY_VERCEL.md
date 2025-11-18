# ⚠️ Deploy no Vercel (NÃO RECOMENDADO)

Guia para deploy no Vercel - **Use Render.com ao invés!**

---

## ❌ Por que NÃO usar Vercel para este projeto?

1. **Serverless Functions** - Timeout de 10s (gratuito) ou 60s (pago)
2. **Upload de arquivos** - Limite de 4.5MB por request
3. **OCR/Tesseract** - Binários não disponíveis no ambiente serverless
4. **Cold starts** - Primeira requisição sempre lenta
5. **Custo** - Pode ficar caro com muitas requisições

---

## 🚀 Se AINDA ASSIM quiser tentar Vercel

### Limitações que você terá:

- ❌ Upload de comprovantes grandes (>4.5MB) não funcionará
- ❌ OCR pode não funcionar (Tesseract não disponível)
- ❌ Timeout em requisições longas
- ❌ Cold start em toda requisição após inatividade

### Passo a Passo:

1. **Instalar Vercel CLI**
```bash
npm install -g vercel
```

2. **Login**
```bash
vercel login
```

3. **Configurar Variáveis de Ambiente**
```bash
vercel env add SUPABASE_URL
vercel env add SUPABASE_KEY
```

4. **Deploy**
```bash
vercel --prod
```

### Problemas Esperados:

1. **OCR não funciona**
   - Tesseract precisa de binários do sistema
   - Não disponível no ambiente serverless da Vercel

2. **Upload falha**
   - Arquivos >4.5MB são rejeitados
   - Timeout em processamento de PDFs grandes

3. **Performance ruim**
   - Cold start em toda requisição
   - Latência alta

---

## ✅ RECOMENDAÇÃO FORTE

**Use Render.com ao invés!**

Veja o guia: `DEPLOY_RENDER.md`

Render.com é:
- ✅ Gratuito
- ✅ Suporta FastAPI perfeitamente
- ✅ Sem limitações de upload
- ✅ OCR funciona
- ✅ Performance melhor

---

## 🔄 Alternativas Melhores que Vercel

1. **Render.com** ⭐⭐⭐⭐⭐ (MELHOR)
2. **Railway.app** ⭐⭐⭐⭐
3. **Fly.io** ⭐⭐⭐⭐
4. **Heroku** ⭐⭐⭐ (pago)
5. **Vercel** ⭐⭐ (não recomendado para este caso)

---

**Conclusão:** Não use Vercel para este projeto. Use Render.com! 🚀
