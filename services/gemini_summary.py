import google.generativeai as genai
import os
import json

class GeminiService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash-lite') # Using user-specified 2.5 Flash Lite model
        else:
            self.model = None

    def is_available(self):
        return self.model is not None

    def summarize(self, text):
        if not self.model:
            return "Gemini API Key not provided."
        
        try:
            prompt = f"""
            You are an expert web content analyst. Analyze the following text scraped from a website and provide a comprehensive report.
            
            Please structure your response exactly as follows:
            
            ### 🎯 What is this website about?
            (Provide a concise 1-2 sentence description of the main purpose or topic of this page)
            
            ### 📝 Key Information Contained
            (Summarize the main content, facts, and details found on the page. Be specific and informative.)
            
            ### 🔑 Key Takeaways
            (List 3-5 most important points or insights from this page)
            
            ---
            Scraped Text Content:
            {text[:15000]}
            """
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating summary: {str(e)}"

    def extract_entities(self, text):
        if not self.model:
            return {}
        
        try:
            prompt = f"""
            Extract the following entities from the text if present: 
            - Names
            - Emails
            - Phone Numbers
            - Products/Prices
            
            Return as JSON.
            
            Text: {text[:10000]}
            """
            response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            return json.loads(response.text)
        except Exception as e:
            return {"error": str(e)}
