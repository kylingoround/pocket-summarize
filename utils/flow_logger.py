"""
Comprehensive logging utility for YouTube summarizer flow.
Captures all node outputs and can save to file for analysis.
"""

import logging
import sys
from datetime import datetime
from typing import Optional

class FlowLogger:
    """Logger that captures both console output and saves to file."""
    
    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file or f"flow_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration."""
        # Create logger
        self.logger = logging.getLogger('YouTubeSummarizer')
        self.logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(message)s')
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # File handler
        file_handler = logging.FileHandler(self.log_file, mode='w', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_format = logging.Formatter('%(asctime)s - %(message)s')
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
        
        # Log start
        self.logger.info("=" * 80)
        self.logger.info(f"YouTube Summarizer Flow Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 80)
    
    def log_node_start(self, node_name: str, input_data: dict):
        """Log when a node starts processing."""
        self.logger.info(f"🚀 {node_name}: Starting execution")
        if input_data:
            for key, value in input_data.items():
                if isinstance(value, str):
                    self.logger.info(f"   📄 {key}: {len(value):,} characters")
                elif isinstance(value, list):
                    self.logger.info(f"   📋 {key}: {len(value)} items")
                else:
                    self.logger.info(f"   📊 {key}: {value}")
    
    def log_node_end(self, node_name: str, output_data: dict):
        """Log when a node completes processing."""
        self.logger.info(f"✅ {node_name}: Completed successfully")
        if output_data:
            for key, value in output_data.items():
                if isinstance(value, str):
                    self.logger.info(f"   📄 {key}: {len(value):,} characters")
                elif isinstance(value, list):
                    self.logger.info(f"   📋 {key}: {len(value)} items")
                else:
                    self.logger.info(f"   📊 {key}: {value}")
    
    def log_llm_call(self, node_name: str, call_num: int, total_calls: int, 
                    prompt_size: int, estimated_tokens: int, success: bool, 
                    duration: float, error: str = None):
        """Log individual LLM calls."""
        status = "✅" if success else "❌"
        self.logger.info(f"{status} {node_name}: LLM call {call_num}/{total_calls} "
                        f"(prompt: {prompt_size:,} chars, ~{estimated_tokens:,} tokens, "
                        f"{duration:.2f}s)")
        if error:
            self.logger.info(f"   💥 Error: {error}")
    
    def log_error(self, node_name: str, error: str, context: dict = None):
        """Log errors with context."""
        self.logger.info(f"❌ {node_name}: ERROR - {error}")
        if context:
            for key, value in context.items():
                self.logger.info(f"   🔍 {key}: {value}")
    
    def log_summary(self, summary_data: dict):
        """Log final summary statistics."""
        self.logger.info("=" * 80)
        self.logger.info("📊 FINAL SUMMARY")
        self.logger.info("=" * 80)
        
        for key, value in summary_data.items():
            if isinstance(value, dict):
                self.logger.info(f"📋 {key}:")
                for sub_key, sub_value in value.items():
                    self.logger.info(f"   {sub_key}: {sub_value}")
            elif isinstance(value, list):
                self.logger.info(f"📋 {key}: {len(value)} items")
            else:
                self.logger.info(f"📊 {key}: {value}")
        
        self.logger.info("=" * 80)
        self.logger.info(f"📁 Log saved to: {self.log_file}")
        self.logger.info("=" * 80)

# Global logger instance
_global_logger = None

def get_logger() -> FlowLogger:
    """Get the global logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = FlowLogger()
    return _global_logger

def setup_logging(log_file: Optional[str] = None):
    """Setup global logging."""
    global _global_logger
    _global_logger = FlowLogger(log_file)
    return _global_logger
