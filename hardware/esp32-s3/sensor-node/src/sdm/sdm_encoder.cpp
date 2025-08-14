#include "sdm.h"
#include <cmath>

SDMEncoder::SDMEncoder(SparseDistributedMemory* sdm_instance) : sdm(sdm_instance) {
    // Initialize encoder with SDM instance
}

std::vector<uint8_t> SDMEncoder::encodeText(const String& text) {
    // Simple character-based encoding for demonstration
    // In practice, you'd use more sophisticated NLP encoding
    
    std::vector<uint8_t> encoded(sdm->config.vector_dim, 0);
    
    // Hash-based character encoding
    for (int i = 0; i < text.length() && i < sequence_length; i++) {
        char c = text[i];
        
        // Simple hash function for character positioning
        uint16_t hash1 = (c * 17 + i * 31) % sdm->config.vector_dim;
        uint16_t hash2 = (c * 23 + i * 47) % sdm->config.vector_dim;
        uint16_t hash3 = (c * 41 + i * 53) % sdm->config.vector_dim;
        
        // Set multiple bits per character for redundancy
        encoded[hash1] = 1;
        encoded[hash2] = 1;
        encoded[hash3] = 1;
    }
    
    return encoded;
}

String SDMEncoder::decodeText(const std::vector<uint8_t>& vector) {
    // This is a simplified decoder - real implementation would be more complex
    // For now, return a placeholder indicating successful decoding
    
    uint16_t active_bits = 0;
    for (uint8_t bit : vector) {
        if (bit) active_bits++;
    }
    
    return "Decoded_" + String(active_bits) + "_bits";
}

std::vector<uint8_t> SDMEncoder::encodeFloat(float value, float min_val, float max_val) {
    std::vector<uint8_t> encoded(sdm->config.vector_dim, 0);
    
    // Normalize value to [0, 1] range
    float normalized = (value - min_val) / (max_val - min_val);
    normalized = constrain(normalized, 0.0f, 1.0f);
    
    // Convert to binary representation using thermometer encoding
    uint16_t position = static_cast<uint16_t>(normalized * (sdm->config.vector_dim - 1));
    
    // Set bits from 0 to position (thermometer encoding)
    for (uint16_t i = 0; i <= position && i < sdm->config.vector_dim; i++) {
        encoded[i] = 1;
    }
    
    return encoded;
}

float SDMEncoder::decodeFloat(const std::vector<uint8_t>& vector, float min_val, float max_val) {
    // Find the highest set bit position (thermometer decoding)
    uint16_t highest_bit = 0;
    for (uint16_t i = 0; i < vector.size(); i++) {
        if (vector[i] == 1) {
            highest_bit = i;
        }
    }
    
    // Convert back to normalized value
    float normalized = static_cast<float>(highest_bit) / (sdm->config.vector_dim - 1);
    
    // Scale back to original range
    return min_val + normalized * (max_val - min_val);
}

std::vector<uint8_t> SDMEncoder::encodeSequence(const std::vector<float>& sequence) {
    std::vector<uint8_t> encoded(sdm->config.vector_dim, 0);
    
    if (sequence.empty()) return encoded;
    
    // Encode sequence using distributed representation
    uint16_t bits_per_element = sdm->config.vector_dim / sequence_length;
    
    for (size_t i = 0; i < sequence.size() && i < sequence_length; i++) {
        // Normalize each element
        float normalized = (sequence[i] + 1.0f) / 2.0f;  // Assume [-1, 1] range
        normalized = constrain(normalized, 0.0f, 1.0f);
        
        // Set bits in allocated segment
        uint16_t start_bit = i * bits_per_element;
        uint16_t num_bits = static_cast<uint16_t>(normalized * bits_per_element);
        
        for (uint16_t j = 0; j < num_bits && (start_bit + j) < sdm->config.vector_dim; j++) {
            encoded[start_bit + j] = 1;
        }
    }
    
    return encoded;
}

std::vector<float> SDMEncoder::decodeSequence(const std::vector<uint8_t>& vector) {
    std::vector<float> sequence;
    
    uint16_t bits_per_element = sdm->config.vector_dim / sequence_length;
    
    for (uint16_t i = 0; i < sequence_length; i++) {
        uint16_t start_bit = i * bits_per_element;
        uint16_t active_bits = 0;
        
        // Count active bits in this segment
        for (uint16_t j = 0; j < bits_per_element && (start_bit + j) < vector.size(); j++) {
            if (vector[start_bit + j] == 1) {
                active_bits++;
            }
        }
        
        // Convert back to normalized value
        float normalized = static_cast<float>(active_bits) / bits_per_element;
        float value = normalized * 2.0f - 1.0f;  // Scale to [-1, 1]
        
        sequence.push_back(value);
    }
    
    return sequence;
}