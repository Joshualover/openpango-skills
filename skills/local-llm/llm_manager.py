"""
Local LLM Manager for OpenPango
Support for Ollama, vLLM, and other local inference backends
"""

import json
import os
import requests
from typing import Optional, List, Dict, Any


class LocalLLMManager:
    """Local LLM inference manager supporting multiple backends."""
    
    BACKENDS = {
        "ollama": {"default_port": 11434, "api_path": "/api/generate"},
        "vllm": {"default_port": 8000, "api_path": "/v1/completions"},
        "llama_cpp": {"default_port": 8080, "api_path": "/completion"},
    }
    
    def __init__(self, backend: str = "ollama", model: str = "llama3",
                 host: str = "localhost", port: int = None):
        self.backend = backend
        self.model = model
        self.host = host
        self.port = port or self.BACKENDS.get(backend, {}).get("default_port", 11434)
        self.base_url = f"http://{self.host}:{self.port}"
    
    def _format_prompt_chatml(self, messages: List[Dict]) -> str:
        """Format messages using ChatML format."""
        formatted = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            formatted += f"<|im_start|>{role}\n{content}<|im_end|>\n"
        formatted += "<|im_start|>assistant\n"
        return formatted
    
    def _format_prompt_llama3(self, messages: List[Dict]) -> str:
        """Format messages using Llama 3 format."""
        formatted = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                formatted += f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{content}<|eot_id|>"
            elif role == "user":
                formatted += f"<|start_header_id|>user<|end_header_id|>\n\n{content}<|eot_id|>"
            elif role == "assistant":
                formatted += f"<|start_header_id|>assistant<|end_header_id|>\n\n{content}<|eot_id|>"
        formatted += "<|start_header_id|>assistant<|end_header_id|>\n\n"
        return formatted
    
    def _format_prompt(self, messages: List[Dict], prompt_format: str = None) -> str:
        """Format prompt based on model type."""
        if prompt_format == "chatml":
            return self._format_prompt_chatml(messages)
        elif prompt_format == "llama3" or "llama" in self.model.lower():
            return self._format_prompt_llama3(messages)
        else:
            # Default: simple concatenation
            return "\n".join([f"{m['role']}: {m['content']}" for m in messages])
    
    def generate(self, prompt: str, max_tokens: int = 1024, 
                temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate text completion.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        
        Returns:
            Generation result with text and metadata
        """
        if self.backend == "ollama":
            return self._ollama_generate(prompt, max_tokens, temperature)
        elif self.backend == "vllm":
            return self._vllm_generate(prompt, max_tokens, temperature)
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")
    
    def _ollama_generate(self, prompt: str, max_tokens: int, 
                        temperature: float) -> Dict[str, Any]:
        """Generate using Ollama API."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "text": result.get("response", ""),
                "model": self.model,
                "backend": self.backend,
                "total_tokens": result.get("eval_count", 0),
                "prompt_tokens": result.get("prompt_eval_count", 0)
            }
        except requests.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "backend": self.backend
            }
    
    def _vllm_generate(self, prompt: str, max_tokens: int,
                      temperature: float) -> Dict[str, Any]:
        """Generate using vLLM OpenAI-compatible API."""
        url = f"{self.base_url}/v1/completions"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            
            choices = result.get("choices", [])
            text = choices[0].get("text", "") if choices else ""
            usage = result.get("usage", {})
            
            return {
                "success": True,
                "text": text,
                "model": self.model,
                "backend": self.backend,
                "total_tokens": usage.get("total_tokens", 0),
                "prompt_tokens": usage.get("prompt_tokens", 0)
            }
        except requests.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "backend": self.backend
            }
    
    def chat(self, messages: List[Dict], max_tokens: int = 1024,
            temperature: float = 0.7, prompt_format: str = None) -> Dict[str, Any]:
        """
        Chat completion with message history.
        
        Args:
            messages: List of message dicts with role/content
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            prompt_format: Format to use (chatml, llama3, auto)
        
        Returns:
            Chat response with text and metadata
        """
        formatted_prompt = self._format_prompt(messages, prompt_format)
        return self.generate(formatted_prompt, max_tokens, temperature)
    
    def list_models(self) -> List[str]:
        """List available models on the backend."""
        if self.backend == "ollama":
            try:
                response = requests.get(f"{self.base_url}/api/tags", timeout=10)
                response.raise_for_status()
                result = response.json()
                return [model["name"] for model in result.get("models", [])]
            except:
                return []
        elif self.backend == "vllm":
            try:
                response = requests.get(f"{self.base_url}/v1/models", timeout=10)
                response.raise_for_status()
                result = response.json()
                return [model["id"] for model in result.get("data", [])]
            except:
                return []
        return []
    
    def health_check(self) -> Dict[str, Any]:
        """Check if the backend is healthy."""
        try:
            if self.backend == "ollama":
                response = requests.get(f"{self.base_url}/api/tags", timeout=5)
                return {
                    "healthy": response.status_code == 200,
                    "backend": self.backend,
                    "url": self.base_url
                }
            elif self.backend == "vllm":
                response = requests.get(f"{self.base_url}/health", timeout=5)
                return {
                    "healthy": response.status_code == 200,
                    "backend": self.backend,
                    "url": self.base_url
                }
        except Exception as e:
            return {
                "healthy": False,
                "backend": self.backend,
                "url": self.base_url,
                "error": str(e)
            }
        return {"healthy": False, "backend": self.backend}


# CLI integration
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Local LLM Manager CLI")
    parser.add_argument("--backend", default="ollama", choices=["ollama", "vllm"])
    parser.add_argument("--model", default="llama3", help="Model name")
    parser.add_argument("--host", default="localhost", help="Server host")
    parser.add_argument("--port", type=int, help="Server port")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate text")
    gen_parser.add_argument("prompt", help="Input prompt")
    gen_parser.add_argument("--max-tokens", type=int, default=512)
    gen_parser.add_argument("--temp", type=float, default=0.7)
    
    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Chat completion")
    chat_parser.add_argument("message", help="User message")
    chat_parser.add_argument("--system", default="You are a helpful assistant")
    
    # List models
    subparsers.add_parser("models", help="List available models")
    
    # Health check
    subparsers.add_parser("health", help="Check backend health")
    
    args = parser.parse_args()
    
    llm = LocalLLMManager(
        backend=args.backend,
        model=args.model,
        host=args.host,
        port=args.port
    )
    
    if args.command == "generate":
        result = llm.generate(args.prompt, args.max_tokens, args.temp)
        if result["success"]:
            print(result["text"])
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
    
    elif args.command == "chat":
        messages = [
            {"role": "system", "content": args.system},
            {"role": "user", "content": args.message}
        ]
        result = llm.chat(messages)
        if result["success"]:
            print(result["text"])
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
    
    elif args.command == "models":
        models = llm.list_models()
        if models:
            print("Available models:")
            for model in models:
                print(f"  - {model}")
        else:
            print("No models found or backend unavailable")
    
    elif args.command == "health":
        result = llm.health_check()
        status = "✅ Healthy" if result["healthy"] else "❌ Unhealthy"
        print(f"{status} - {result['backend']} @ {result['url']}")
        if "error" in result:
            print(f"Error: {result['error']}")


if __name__ == "__main__":
    main()
