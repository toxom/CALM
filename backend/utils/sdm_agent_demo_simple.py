#!/usr/bin/env python3
"""
CALM SDM Agent Demonstration (No matplotlib)
Shows working Sparse Distributed Memory with Swarm Intelligence
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.core.sdm.swarm.swarm_agent import create_camera_ugv_swarm_demo, SDMSwarmAgent
import numpy as np

def demo_swarm_agents():
    """Demonstrate swarm agent communication"""
    print("\n" + "="*60)
    print("CALM - Camera & UGV Swarm Coordination Demo")
    print("="*60)
    
    camera, ugv = create_camera_ugv_swarm_demo()
    
    return camera, ugv

def demo_agent_learning():
    """Demonstrate agent learning from interactions"""
    print("\n" + "="*60)
    print("Agent Learning & Adaptation Demo")
    print("="*60)
    
    agent = SDMSwarmAgent("agent_001", "camera", vector_dim=256, num_locations=500)
    
    print(f"\n🤖 Created Agent: {agent.agent_id}")
    print(f"   Type: {agent.agent_type}")
    print(f"   SDM capacity: {agent.sdm.num_locations} locations")
    
    print(f"\n📹 Simulating detection sequence...")
    
    detections = []
    for i in range(3):
        input_data = np.random.rand(256) * 100
        detection = agent.detect_pattern(input_data)
        detections.append(detection)
        
        print(f"\n   Detection {i+1}:")
        print(f"      Classification: {detection['classification']}")
        print(f"      Confidence: {detection['confidence']:.3f}")
    
    print(f"\n✅ Agent successfully processed {len(detections)} detections!")
    
    return agent, detections

def show_architecture():
    print("\n" + "="*60)
    print("CALM Architecture Summary")
    print("="*60)
    print("""
📁 Project Structure:
   ├── backend/core/sdm/          # Core SDM implementation
   │   ├── memory.py              # Binary SDM with signed counters
   │   ├── swarm/                 # Multi-agent coordination
   │   │   └── swarm_agent.py     # SDM-based agents
   │   ├── hierarchy/             # Complexity analysis
   │   └── optimization/          # Performance optimization

🧠 Key Features:
   ✓ Sparse Distributed Memory (3% sparsity optimal)
   ✓ Binary vectors with signed integer counters
   ✓ Hamming distance-based recall
   ✓ Swarm intelligence (camera-UGV coordination)
   ✓ Reinforcement learning integration
   ✓ Continual learning (no catastrophic forgetting)
    """)

if __name__ == "__main__":
    print("\n🚀 CALM - Continual Associative Learning Model")
    print("    SDM Agent Demonstration\n")
    
    show_architecture()
    camera, ugv = demo_swarm_agents()
    agent, detections = demo_agent_learning()
    
    print("\n" + "="*60)
    print("✅ All Demonstrations Complete!")
    print("="*60)
