#!/usr/bin/env python3
"""
Simple Visual Summary: The Mathematical Identity
"""

import matplotlib.pyplot as plt
import numpy as np

def create_simple_summary():
    """Create a simple visual summary of the mathematical relationship"""
    
    # Create figure with mathematical explanation
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Left side: Formula comparison
    ax1.text(0.5, 0.9, "MATHEMATICAL IDENTITY", ha='center', va='center', 
             fontsize=20, fontweight='bold', transform=ax1.transAxes)
    
    ax1.text(0.5, 0.75, "Method 1: Covariance/Variance (Your Approach)", 
             ha='center', va='center', fontsize=14, fontweight='bold', 
             color='blue', transform=ax1.transAxes)
    
    ax1.text(0.5, 0.65, r"$\beta = \frac{Cov(Stock, Market)}{Var(Market)}$", 
             ha='center', va='center', fontsize=16, transform=ax1.transAxes)
    
    ax1.text(0.5, 0.55, r"$\beta = \frac{\sum_{i=1}^{n}(Stock_i - \overline{Stock})(Market_i - \overline{Market})}{\sum_{i=1}^{n}(Market_i - \overline{Market})^2} \times \frac{n-1}{n-1}$", 
             ha='center', va='center', fontsize=12, transform=ax1.transAxes)
    
    ax1.text(0.5, 0.4, "Method 2: Linear Regression (My Approach)", 
             ha='center', va='center', fontsize=14, fontweight='bold', 
             color='red', transform=ax1.transAxes)
    
    ax1.text(0.5, 0.3, r"$Stock_i = \alpha + \beta \times Market_i + \epsilon_i$", 
             ha='center', va='center', fontsize=16, transform=ax1.transAxes)
    
    ax1.text(0.5, 0.2, r"$\beta = \frac{\sum_{i=1}^{n}(Market_i - \overline{Market})(Stock_i - \overline{Stock})}{\sum_{i=1}^{n}(Market_i - \overline{Market})^2}$", 
             ha='center', va='center', fontsize=12, transform=ax1.transAxes)
    
    ax1.text(0.5, 0.05, "IDENTICAL FORMULAS! ✅", 
             ha='center', va='center', fontsize=18, fontweight='bold', 
             color='green', transform=ax1.transAxes)
    
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.axis('off')
    
    # Right side: Practical example
    np.random.seed(42)
    market = np.random.normal(0.01, 0.04, 50)
    stock = 0.005 + 1.5 * market + np.random.normal(0, 0.02, 50)
    
    # Calculate beta both ways
    cov_beta = np.cov(stock, market)[0,1] / np.var(market, ddof=1)
    from scipy.stats import linregress
    reg_beta, alpha, r_val, p_val, std_err = linregress(market, stock)
    
    ax2.scatter(market, stock, alpha=0.7, color='blue', s=50)
    
    # Regression line
    x_line = np.linspace(market.min(), market.max(), 100)
    y_line = alpha + reg_beta * x_line
    ax2.plot(x_line, y_line, 'r-', linewidth=2)
    
    ax2.set_xlabel('Market Returns', fontsize=12)
    ax2.set_ylabel('Stock Returns', fontsize=12)
    ax2.set_title('Both Methods Give Identical Results', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # Add results
    ax2.text(0.05, 0.95, f'Covariance Method: β = {cov_beta:.6f}', 
             transform=ax2.transAxes, fontsize=12, 
             bbox=dict(boxstyle='round', facecolor='lightblue'))
    
    ax2.text(0.05, 0.85, f'Regression Method: β = {reg_beta:.6f}', 
             transform=ax2.transAxes, fontsize=12,
             bbox=dict(boxstyle='round', facecolor='lightcoral'))
    
    ax2.text(0.05, 0.75, f'Difference: {abs(cov_beta-reg_beta):.10f}', 
             transform=ax2.transAxes, fontsize=12, fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='lightgreen'))
    
    plt.tight_layout()
    plt.savefig('beta_methods_identity.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return cov_beta, reg_beta

if __name__ == "__main__":
    print("🎯 CREATING VISUAL SUMMARY OF MATHEMATICAL IDENTITY")
    print("="*60)
    
    cov_beta, reg_beta = create_simple_summary()
    
    print(f"\n✅ VISUAL DEMONSTRATION COMPLETE!")
    print(f"Covariance/Variance β: {cov_beta:.10f}")
    print(f"Linear Regression β:   {reg_beta:.10f}")
    print(f"Difference:            {abs(cov_beta-reg_beta):.2e}")
    print(f"\n💡 Both methods are mathematically identical!")
    print(f"📊 Chart saved as 'beta_methods_identity.png'")