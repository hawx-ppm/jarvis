import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from telegram.ext import Application, CommandHandler, MessageHandler, filters
from transformers import pipeline
from docx import Document
import asyncio

# Função para ler o conteúdo do arquivo Word
def read_word_file(file_path):
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

# Função para carregar o modelo de NLP para responder perguntas
def load_nlp_model():
    return pipeline(
        'question-answering', 
        model='distilbert-base-uncased-distilled-squad',
        clean_up_tokenization_spaces=True  # Define explicitamente o parâmetro
    )
    
# Função para responder perguntas usando o modelo de NLP
def answer_question(question, context, nlp_model):
    result = nlp_model(question=question, context=context)
    return result['answer']

# Função que será chamada quando o comando /start for enviado
async def start(update, context):
    await update.message.reply_text('Olá! Eu sou o bot do Popmundo. Como posso ajudar?')

# Função que será chamada quando o comando /help for enviado
async def help_command(update, context):
    await update.message.reply_text('Você pode me perguntar sobre o jogo Popmundo!')

# Função que será chamada para processar mensagens de texto
async def handle_message(update, context, document_text, nlp_model):
    user_message = update.message.text
    response = answer_question(user_message, document_text, nlp_model)
    await update.message.reply_text(response)

# Função principal para configurar e rodar o bot
async def main():
    # Leia o conteúdo do arquivo Word
    document_text = read_word_file('resources/popmundo_guide.docx')

    # Carregue o modelo de NLP
    nlp_model = load_nlp_model()

    # Crie o Application e passe o token do bot
    application = Application.builder().token('6898883366:AAGgyFo4a2r3jVpNLuMe5NG0xg-SUDkVG9E').build()

    # Configure os handlers para os comandos e mensagens de texto
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lambda update, context: handle_message(update, context, document_text, nlp_model)))

    # Inicie o bot
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await application.stop()

if __name__ == '__main__':
    try:
        # Tente rodar no loop de eventos padrão
        asyncio.run(main())
    except RuntimeError as e:
        if str(e) == "Cannot close a running event loop":
            # Se já existir um loop rodando, use ele
            loop = asyncio.get_running_loop()
            loop.create_task(main())
        else:
            raise
