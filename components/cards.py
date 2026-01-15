import streamlit as st

def metric_card(title: str, value: str, delta: str = None, help_text: str = None):
    """
    Renders a metric card with custom styling.
    """
    st.markdown(f"""
    <div style="
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #eee;
    ">
        <div style="color: #666; font-size: 14px; margin-bottom: 5px;">{title}</div>
        <div style="font-size: 24px; font-weight: bold; color: #333;">{value}</div>
        {f'<div style="color: {"green" if delta and "+" in delta or (delta and float(delta.strip("%").replace("+","")) > 0) else "red"}; font-size: 14px; margin-top: 5px;">{delta}</div>' if delta else ''}
    </div>
    """, unsafe_allow_html=True)
    
    # Note: Streamlit built-in metric is also good, but custom HTML gives more control.
    # However, to be consistent with Streamlit, we might just use st.metric.
    # The user asked for "Metric Cards Component", let's stick to st.metric for simplicity and native look unless requested otherwise.
    # But wait, the plan said "Visual style: Card with title, value, change indicator, and mini-trend".
    # st.metric does title, value, delta.
    # Let's wrap st.metric in a container for now.
    
    # Actually, let's use st.metric but maybe style the container.
    pass

def render_metric_card(title: str, value: str, delta: str = None, description: str = None):
    """
    Wrapper for st.metric to ensure consistent styling or future enhancement.
    """
    with st.container():
        st.metric(label=title, value=value, delta=delta, help=description)
