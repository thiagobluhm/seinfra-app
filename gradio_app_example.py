from gradio_pdf import PDF
import gradio as gr

# Interface do Gradio
with gr.Blocks() as demo:
    gr.Markdown("### 📑 Clipapptor - IA*")
    
    with gr.Row():
        with gr.Column(scale=1):  # Lado esquerdo

            uploaded_pdf = PDF(label="📤 Faça upload do PDF", interactive=True)                   
            
        with gr.Column(scale=1):  # Lado direito
            name = gr.Textbox(label = "📄 Caminho do arquivo.")
            uploaded_pdf.upload(lambda f: f, inputs=uploaded_pdf, outputs=name)
            #output_pdf_view = gr.HTML()  # Visualização do PDF         
            process_button = gr.Button(f"📄 Processar PDF")     
            #log_output = gr.Textbox(label="🖥️ Terminal", lines=15, interactive=False)  # Terminal            
            output_docx_view = gr.File(label="📋 Baixar Clipping Gerado")    

        #uploaded_pdf.change(fn=update_pdf_view, inputs=[uploaded_pdf], outputs=[output_pdf_view])
        #process_button.click(fn=process_pdf, inputs=[uploaded_pdf], outputs=[uploaded_pdf, output_docx_view])

# Iniciar monitor de logs em background
# log_thread = Thread(target=monitor_logs, args=(log_output,), daemon=True)
# log_thread.start()

# Executar interface
demo.launch()