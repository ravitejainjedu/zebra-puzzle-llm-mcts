import pytest
from src.state import ZebraState

def test_initial_state_valid():
    state = ZebraState()
    assert state.is_valid() == True
