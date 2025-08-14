# backend/core/sdm/swarm/swarm_agent.py

import numpy as np
from typing import Dict, List, Optional
from enum import Enum
from ..memory import SparseDistributedMemory
import time

class MessagePriority(Enum):
    LOW = 1
    NORMAL = 2  
    HIGH = 3
    CRITICAL = 4

class CommunicationMode(Enum):
    LIGHTWEIGHT = "lightweight_sharing"
    HIGH_FIDELITY = "high_fidelity_sharing"

class SwarmMessage:
    def __init__(self, sender_id: str, pattern: np.ndarray, 
                 priority: MessagePriority, metadata: Dict):
        self.sender_id = sender_id
        self.pattern = pattern
        self.priority = priority
        self.metadata = metadata
        self.timestamp = time.time()

class SDMSwarmAgent:
    def __init__(self, agent_id: str, agent_type: str, 
                 vector_dim: int = 512, num_locations: int = 1000):
        self.agent_id = agent_id
        self.agent_type = agent_type  # "camera", "ugv", "sensor", etc.
        
        # Core SDM module
        self.sdm = SparseDistributedMemory(vector_dim, num_locations)
        
        # Swarm communication
        self.connected_agents = {}
        self.message_queue = []
        
        # RL state tracking
        self.current_task = None
        self.computational_load = 0.0
        self.last_communication_mode = CommunicationMode.LIGHTWEIGHT
        
        # Agent-specific thresholds
        self.threat_threshold = 30  # Hamming distance
        self.confidence_threshold = 0.8
        
    def get_swarm_state(self):
        """Get current state for RL decision making"""
        return {
            'position': self.get_position(),
            'task': self.current_task,
            'events': self.detect_events(),
            'load': self.computational_load,
            'queue_size': len(self.message_queue)
        }
    
    def detect_pattern(self, input_data: np.ndarray) -> Dict:
        """Detect and classify patterns using SDM"""
        # Store pattern in SDM
        pattern_vector = self.preprocess_input(input_data)
        self.sdm.write(pattern_vector, strength=1)
        
        # Retrieve similar patterns for classification
        recalled_pattern, confidence = self.sdm.read(pattern_vector)
        
        # Classify based on similarity to known patterns
        classification = self.classify_pattern(recalled_pattern, confidence)
        
        return {
            'pattern': pattern_vector,
            'classification': classification,
            'confidence': confidence,
            'timestamp': time.time()
        }
    
    def decide_communication_mode(self, detection_result: Dict) -> CommunicationMode:
        """Use RL-like policy to decide communication mode"""
        state = self.get_swarm_state()
        
        # Simple rule-based policy (could be replaced with trained RL)
        if (detection_result['confidence'] > 0.9 and 
            'THREAT' in detection_result['classification']):
            return CommunicationMode.HIGH_FIDELITY
        elif self.computational_load > 0.8:
            return CommunicationMode.LIGHTWEIGHT
        else:
            return CommunicationMode.LIGHTWEIGHT
    
    def broadcast_detection(self, detection_result: Dict):
        """Broadcast detection to swarm based on communication mode"""
        mode = self.decide_communication_mode(detection_result)
        
        if mode == CommunicationMode.HIGH_FIDELITY:
            # Forward complete pattern + metadata
            message = SwarmMessage(
                sender_id=self.agent_id,
                pattern=detection_result['pattern'],
                priority=MessagePriority.HIGH,
                metadata={
                    'classification': detection_result['classification'],
                    'confidence': detection_result['confidence'],
                    'full_context': True,
                    'sender_type': self.agent_type
                }
            )
        else:
            # Forward lightweight summary
            compressed_pattern = self.compress_pattern(detection_result['pattern'])
            message = SwarmMessage(
                sender_id=self.agent_id,
                pattern=compressed_pattern,
                priority=MessagePriority.NORMAL,
                metadata={
                    'classification': detection_result['classification'],
                    'confidence': detection_result['confidence'],
                    'full_context': False,
                    'sender_type': self.agent_type
                }
            )
        
        self.send_to_swarm(message)
    
    def process_swarm_message(self, message: SwarmMessage) -> Dict:
        """Process incoming message from swarm"""
        print(f"{self.agent_id}: Received message from {message.sender_id}")
        
        # Calculation of relevance using Hamming distance
        if hasattr(self, 'current_patterns'):
            relevance_scores = []
            for known_pattern in self.current_patterns:
                distance = np.sum(known_pattern != message.pattern)
                relevance_scores.append(distance)
            
            min_distance = min(relevance_scores) if relevance_scores else float('inf')
        else:
            min_distance = float('inf')
        
        # Response based on relevance and priority
        response = {
            'relevant': min_distance < self.threat_threshold,
            'distance': min_distance,
            'requires_action': message.priority.value >= MessagePriority.HIGH.value,
            'classification': message.metadata.get('classification', 'UNKNOWN')
        }
        
        if response['relevant'] and response['requires_action']:
            self.trigger_response_action(message, response)
        
        return response
    
    def trigger_response_action(self, message: SwarmMessage, analysis: Dict):
        """Take action based on swarm communication"""
        print(f"{self.agent_id}: Taking action based on {message.sender_id}'s message")
        
        if self.agent_type == "ugv":
            if "THREAT" in analysis['classification']:
                print(f"{self.agent_id}: THREAT DETECTED! Switching to investigate mode")
                self.current_task = "INVESTIGATE"
                # Requesting high-fidelity data if needed
                if not message.metadata.get('full_context', False):
                    self.request_high_fidelity_update(message.sender_id)
        
        elif self.agent_type == "camera":
            if message.sender_id.startswith("ugv"):
                print(f"{self.agent_id}: UGV requesting assistance, adjusting monitoring")
                # Adjusting monitoring parameters based on UGV needs
                self.adjust_monitoring_sensitivity()
    
    def request_high_fidelity_update(self, target_agent_id: str):
        """Request detailed information from specific agent"""
        request_message = SwarmMessage(
            sender_id=self.agent_id,
            pattern=np.array([]),  # Empty pattern for request
            priority=MessagePriority.HIGH,
            metadata={
                'request_type': 'high_fidelity_update',
                'requesting_agent': self.agent_id,
                'target_classification': 'ALL_THREATS'
            }
        )
        print(f"{self.agent_id}: Requesting high-fidelity update from {target_agent_id}")
        # Forward to specific agent (implementation depends on communication layer)
    
    def learn_from_swarm_interaction(self, message: SwarmMessage, outcome: str):
        """Update SDM based on swarm interaction outcomes"""
        # Storing successful interaction patterns for future use
        if outcome == "SUCCESS":
            interaction_pattern = self.encode_interaction(message)
            self.sdm.write(interaction_pattern, strength=5)  # Reinforce successful patterns
            print(f"{self.agent_id}: Learning successful interaction pattern")
    
    # Utility methods
    def preprocess_input(self, input_data: np.ndarray) -> np.ndarray:
        """Convert input to sparse binary vector"""
        if len(input_data.shape) > 1:
            input_data = input_data.flatten()
        
        # Create sparse representation (threshold top 3% of values)
        threshold = np.percentile(input_data, 97)
        sparse_vector = (input_data > threshold).astype(int)
        
        # Ensure minimum sparsity
        if np.sum(sparse_vector) == 0:
            # If no values above threshold, take top 2% of indices
            top_indices = np.argsort(input_data)[-int(len(input_data) * 0.02):]
            sparse_vector[top_indices] = 1
            
        return sparse_vector
    
    def classify_pattern(self, pattern: np.ndarray, confidence: float) -> str:
        """Simple pattern classification"""
        # This would be replaced with more sophisticated classification
        pattern_sum = np.sum(pattern)
        
        if confidence > 0.9:
            if pattern_sum < 10:
                return "BACKGROUND"
            elif pattern_sum < 30:
                return "HUMAN_WALKING" 
            else:
                return "THREAT_DETECTED"
        else:
            return "UNCERTAIN"
    
    def compress_pattern(self, pattern: np.ndarray) -> np.ndarray:
        """Compress pattern for lightweight sharing"""
        # Simple compression: keep only most significant bits
        indices = np.where(pattern == 1)[0]
        return indices[:10]  # keeping only top 10 active indices
    
    def get_position(self):
        """Get agent position (placeholder)"""
        return {"x": 0, "y": 0, "z": 0}
    
    def detect_events(self):
        """Detect current events (placeholder)"""
        return []
    
    def send_to_swarm(self, message: SwarmMessage):
        """Send message to swarm (placeholder)"""
        print(f"{self.agent_id}: Broadcasting {message.priority.name} priority message")
    
    def adjust_monitoring_sensitivity(self):
        """Adjust monitoring parameters"""
        print(f"{self.agent_id}: Adjusting monitoring sensitivity")
        self.threat_threshold = max(20, self.threat_threshold - 5)
    
    def encode_interaction(self, message: SwarmMessage) -> np.ndarray:
        """Encode interaction for learning"""
        # pattern representing this interaction type
        interaction_vector = np.zeros(self.sdm.vector_dim)
        interaction_vector[:len(message.pattern)] = message.pattern[:self.sdm.vector_dim]
        return interaction_vector


# Example usage demonstration
def create_camera_ugv_swarm_demo():
    """Demonstrate camera-UGV swarm interaction"""
    
    # Create agents
    camera = SDMSwarmAgent("camera_001", "camera", vector_dim=256, num_locations=500)
    ugv = SDMSwarmAgent("ugv_001", "ugv", vector_dim=256, num_locations=500)
    
    print("=== Camera-UGV Swarm Demo ===\n")
    
    # Simulate camera detection
    print("1. Camera detects movement...")
    camera_input = (np.random.rand(camera.sdm.vector_dim) < 0.03).astype(int)  # 3% ones
    detection = camera.detect_pattern(camera_input)
    detection['classification'] = "HUMAN_WALKING"  # Override for demo
    
    print(f"   Camera classification: {detection['classification']}")
    print(f"   Confidence: {detection['confidence']:.3f}")
    
    # Camera broadcasts to swarm
    print("\n2. Camera broadcasts to swarm...")
    camera.broadcast_detection(detection)
    
    # simulating UGV receiving message
    print("\n3. UGV processes camera message...")
    message = SwarmMessage(
        sender_id=camera.agent_id,
        pattern=detection['pattern'],
        priority=MessagePriority.NORMAL,
        metadata={'classification': detection['classification'], 'confidence': detection['confidence']}
    )
    
    ugv_response = ugv.process_swarm_message(message)
    print(f"   UGV analysis: relevant={ugv_response['relevant']}, distance={ugv_response['distance']}")
    
    # simulating threat detection
    print("\n4. Camera detects THREAT...")
    threat_input = (np.random.rand(camera.sdm.vector_dim) < 0.03).astype(int)    
    threat_detection = camera.detect_pattern(threat_input)
    threat_detection['classification'] = "THREAT_DETECTED"
    threat_detection['confidence'] = 0.95
    
    print(f"   Threat classification: {threat_detection['classification']}")
    print(f"   High confidence: {threat_detection['confidence']:.3f}")
    
    # Camera sends high-priority message
    print("\n5. Camera sends HIGH PRIORITY alert...")
    threat_message = SwarmMessage(
        sender_id=camera.agent_id,
        pattern=threat_detection['pattern'],
        priority=MessagePriority.HIGH,
        metadata={'classification': threat_detection['classification'], 'confidence': threat_detection['confidence']}
    )
    
    ugv_threat_response = ugv.process_swarm_message(threat_message)
    print(f"   UGV threat response: action required={ugv_threat_response['requires_action']}")
    
    print("\n=== Demo Complete ===")
    
    return camera, ugv

if __name__ == "__main__":
    camera, ugv = create_camera_ugv_swarm_demo()