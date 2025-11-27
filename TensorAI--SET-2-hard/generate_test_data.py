"""
Generate actual test data for hidden test cases.
This will populate the placeholder values with real data from the corrected implementation.
"""

import json
import torch
import numpy as np
from kv_attention import KVCachedMultiHeadAttention, create_sample_input

def generate_test_data():
    # Load test cases from visible test
    with open('test_cases.json', 'r') as f:
        visible_data = json.load(f)
    
    # Load hidden test cases template
    with open('test_cases_hidden.json', 'r') as f:
        hidden_data = json.load(f)
    
    # Get visible test input values
    visible_test = visible_data['test_case']
    visible_query = visible_test['inputs']['query']['values']
    visible_key = visible_test['inputs']['key']['values']
    visible_value = visible_test['inputs']['value']['values']
    
    # Process each hidden test case
    for i, test_case in enumerate(hidden_data['test_cases']):
        print(f"Generating test case {i+1}: {test_case['name']}")
        
        config = test_case['config']
        seed = test_case['seed']
        
        # Set seed for reproducibility BEFORE creating model
        torch.manual_seed(seed)
        np.random.seed(seed)
        
        # Create model
        model = KVCachedMultiHeadAttention(
            d_model=config['d_model'],
            num_heads=config['num_heads'],
            max_cache_len=config['max_cache_len'],
            dropout=config['dropout']
        )
        model.eval()
        
        # Generate or use inputs
        inputs = test_case['inputs']
        cache_data = inputs.get('cache', None)
        
        if i == 0:  # First test - use visible test data
            query = torch.tensor(visible_query, dtype=torch.float32)
            key = torch.tensor(visible_key, dtype=torch.float32)
            value = torch.tensor(visible_value, dtype=torch.float32)
            cache = None
            
            # Update the placeholder values
            test_case['inputs']['query']['values'] = visible_query
            test_case['inputs']['key']['values'] = visible_key
            test_case['inputs']['value']['values'] = visible_value
            
        elif i == 1:  # Second test - uses cache from first test
            # Generate new query/key/value for next token
            batch_size, seq_len, d_model = inputs['query']['shape']
            query, key, value = create_sample_input(batch_size, seq_len, d_model, seed)
            
            # Get cache from previous test output
            prev_cache_key = torch.tensor(hidden_data['test_cases'][0]['expected']['cache']['key']['values'], dtype=torch.float32)
            prev_cache_value = torch.tensor(hidden_data['test_cases'][0]['expected']['cache']['value']['values'], dtype=torch.float32)
            cache = {'key': prev_cache_key, 'value': prev_cache_value}
            
            # Update inputs
            test_case['inputs']['query']['values'] = query.tolist()
            test_case['inputs']['key']['values'] = key.tolist()
            test_case['inputs']['value']['values'] = value.tolist()
            test_case['inputs']['cache']['key']['values'] = prev_cache_key.tolist()
            test_case['inputs']['cache']['value']['values'] = prev_cache_value.tolist()
            
        elif cache_data is not None and isinstance(cache_data, dict) and cache_data.get('key'):
            # Test with cache - need to check if it has placeholders or references another test
            batch_size, seq_len, d_model = inputs['query']['shape']
            query, key, value = create_sample_input(batch_size, seq_len, d_model, seed)
            
            # Check if cache is a placeholder or needs to be generated
            cache_key_values = cache_data['key'].get('values', '_TO_BE_GENERATED_')
            if isinstance(cache_key_values, str):
                # Generate cache for this test
                cache_shape = cache_data['key']['shape']
                cache_key = torch.randn(*cache_shape, dtype=torch.float32)
                cache_value = torch.randn(*cache_shape, dtype=torch.float32)
            else:
                cache_key = torch.tensor(cache_key_values, dtype=torch.float32)
                cache_value = torch.tensor(cache_data['value']['values'], dtype=torch.float32)
            
            cache = {'key': cache_key, 'value': cache_value}
            
            # Update inputs
            test_case['inputs']['query']['values'] = query.tolist()
            test_case['inputs']['key']['values'] = key.tolist()
            test_case['inputs']['value']['values'] = value.tolist()
            test_case['inputs']['cache']['key']['values'] = cache_key.tolist()
            test_case['inputs']['cache']['value']['values'] = cache_value.tolist()
            
        else:  # Other tests - generate random data without cache
            batch_size, seq_len, d_model = inputs['query']['shape']
            query, key, value = create_sample_input(batch_size, seq_len, d_model, seed)
            cache = None
            
            # Update inputs
            test_case['inputs']['query']['values'] = query.tolist()
            test_case['inputs']['key']['values'] = key.tolist()
            test_case['inputs']['value']['values'] = value.tolist()
        
        # Run model
        use_causal_mask = inputs.get('use_causal_mask', True)
        
        with torch.no_grad():
            output, new_cache = model(query, key, value, cache=cache, use_causal_mask=use_causal_mask)
        
        # Update expected outputs
        test_case['expected']['output']['values'] = output.tolist()
        test_case['expected']['cache']['key']['values'] = new_cache['key'].tolist()
        test_case['expected']['cache']['value']['values'] = new_cache['value'].tolist()
        
        print(f"  Output shape: {output.shape}")
        print(f"  Cache key shape: {new_cache['key'].shape}")
    
    # Save updated hidden test cases
    with open('test_cases_hidden_generated.json', 'w') as f:
        json.dump(hidden_data, f, indent=2)
    
    print("\n✓ Generated test cases saved to 'test_cases_hidden_generated.json'")

if __name__ == "__main__":
    generate_test_data()
