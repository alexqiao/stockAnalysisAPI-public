class StockSymbolService:
    def __init__(self):
        """Initialize the service by loading stock data from data/stock.txt"""
        self.stocks = []
        self._load_stock_data()
    
    def _load_stock_data(self):
        """Load stock data from file and parse into list of dictionaries"""
        import os
        
        # Get absolute path to data/stock.txt
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, 'data', 'stock.txt')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Skip the header line
                next(file)
                
                for line in file:
                    line = line.strip()
                    if line:
                        parts = line.split('|')
                        if len(parts) >= 2:
                            symbol = parts[0].strip()
                            name = parts[1].strip()
                            self.stocks.append({
                                'symbol': symbol,
                                'name': name
                            })
        except FileNotFoundError:
            print(f"Warning: {file_path} file not found")
        except Exception as e:
            print(f"Error loading stock data: {e}")
    
    def search(self, keyword):
        """
        Search for stocks where symbol or name contains the keyword (case-insensitive)
        
        Args:
            keyword (str): The search keyword
            
        Returns:
            list: List of matching stock dictionaries (max 10 results)
        """
        if not keyword:
            return []
        
        keyword_lower = keyword.lower()
        results = []
        
        for stock in self.stocks:
            if (keyword_lower in stock['symbol'].lower() or 
                keyword_lower in stock['name'].lower()):
                results.append(stock)
                
                # Limit to 10 results
                if len(results) >= 10:
                    break
        
        return results

# Create singleton instance
stock_symbol_service = StockSymbolService()
