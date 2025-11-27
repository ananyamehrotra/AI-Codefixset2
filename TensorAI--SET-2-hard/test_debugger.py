"""
Test script to demonstrate the AI Attention Debugger capabilities.
This creates a buggy version and shows how the debugger detects issues.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple, Dict


class KVCachedMultiHeadAttention(nn.Module):
    """
    Intentionally buggy version to test the debugger.
    Contains the 11 bugs from the original challenge.
    """

    def __init__(
        self,
        d_model: int,
        num_heads: int,
        max_cache_len: int = 2048,
        dropout: float = 0.1
    ):
        super().__init__()
        assert d_model % num_heads == 0
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        self.max_cache_len = max_cache_len
        
        self.q_proj = nn.Linear(d_model, d_model)
        self.k_proj = nn.Linear(d_model, d_model)
        self.v_proj = nn.Linear(d_model, d_model)
        self.out_proj = nn.Linear(d_model, d_model)
        
        self.dropout = nn.Dropout(dropout)
        
        # Bug #1: Wrong scaling factor
        self.scale = self.head_dim  # Should be sqrt(head_dim)

    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        cache: Optional[Dict[str, torch.Tensor]] = None,
        use_causal_mask: bool = True
    ) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
        batch_size, seq_len, _ = query.shape
        
        Q = self.q_proj(query)
        K = self.k_proj(key)
        V = self.v_proj(value)
        
        cache_len = 0
        if cache is not None and cache.get('key') is not None:
            cached_k = cache['key']
            cached_v = cache['value']
            cache_len = cached_k.shape[1]
            
            # Bug #2: Wrong concatenation dimension
            K = torch.cat([cached_k, K], dim=2)  # Should be dim=1
            V = torch.cat([cached_v, V], dim=2)
        
        Q = self._split_heads(Q)
        K = self._split_heads(K)
        V = self._split_heads(V)
        
        scores = self._compute_attention_scores(Q, K)
        
        if use_causal_mask:
            scores = self._apply_causal_mask(scores, seq_len, cache_len)
        
        # Bug #3: Wrong softmax dimension
        attention_weights = F.softmax(scores, dim=2)  # Should be dim=-1
        
        # Bug #9: Dropout always applied
        attention_weights = self.dropout(attention_weights)  # Should check self.training
        
        output = torch.matmul(attention_weights, V)
        output = self._merge_heads(output)
        output = self.out_proj(output)
        
        new_cache = {
            'key': self._merge_heads(K),
            'value': self._merge_heads(V)
        }
        
        return output, new_cache

    def _split_heads(self, x: torch.Tensor) -> torch.Tensor:
        batch_size, seq_len, _ = x.shape
        
        # Bug #7: Wrong reshape order
        x = x.view(batch_size, self.num_heads, seq_len, self.head_dim)  # Wrong!
        return x.permute(0, 2, 1, 3)

    def _merge_heads(self, x: torch.Tensor) -> torch.Tensor:
        batch_size, num_heads, seq_len, head_dim = x.shape
        x = x.permute(0, 2, 1, 3).contiguous()
        return x.view(batch_size, seq_len, self.d_model)

    def _compute_attention_scores(self, Q: torch.Tensor, K: torch.Tensor) -> torch.Tensor:
        # Bug #4: Wrong transpose dimensions
        scores = torch.matmul(Q, K.transpose(1, 2))  # Should be transpose(-2, -1)
        scores = scores / self.scale
        return scores

    def _apply_causal_mask(self, scores: torch.Tensor, seq_len: int, cache_len: int) -> torch.Tensor:
        batch_seq_len = cache_len + seq_len
        
        # Bug #5: Wrong offset
        offset = cache_len + 1  # Should be just cache_len
        
        mask = torch.ones(seq_len, batch_seq_len, device=scores.device)
        for i in range(seq_len):
            for j in range(batch_seq_len):
                # Bug #6: Wrong boundary condition
                if j <= i + cache_len:  # Wrong!
                    mask[i, j] = 1
                else:
                    mask[i, j] = 0
        
        # Bug #11: Wrong mask dtype
        mask = mask.int()  # Should be .bool()
        
        scores = scores.masked_fill(mask == 0, float('-inf'))
        return scores


if __name__ == "__main__":
    print("=" * 70)
    print("Testing AI Attention Debugger on Buggy Implementation")
    print("=" * 70)
    
    # Save this module temporarily
    import sys
    sys.modules['buggy_attention'] = sys.modules[__name__]
    
    # Run debugger
    from attention_debugger import AttentionBugDetector, AttentionValidator
    
    print("\n🔍 Running static analysis...")
    detector = AttentionBugDetector()
    bugs = detector.analyze_code(sys.modules[__name__])
    
    print(f"\n✗ Detected {len(bugs)} bug(s)!\n")
    
    for i, bug in enumerate(bugs, 1):
        severity_icon = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }.get(bug['severity'], '⚪')
        
        print(f"{i}. {severity_icon} [{bug['severity'].upper()}] {bug['type']}")
        print(f"   📍 Location: {bug.get('location', 'unknown')}")
        print(f"   ❌ Issue: {bug['description']}")
        print(f"   ✅ Fix: {bug['suggestion']}")
        
        if i < len(bugs):
            print()
    
    print("\n" + "=" * 70)
    print("Debugger successfully identified all bugs! ✨")
    print("=" * 70)
