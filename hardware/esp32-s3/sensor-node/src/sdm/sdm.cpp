#include "sdm.h"
#include <random>
#include <algorithm>

SparseDistributedMemory::SparseDistributedMemory() {
    // Default constructor uses default config
}

SparseDistributedMemory::SparseDistributedMemory(const SDMConfig& cfg) : config(cfg) {
    // Constructor with custom config
}

SparseDistributedMemory::~SparseDistributedMemory() {
    // Save state before destruction
    saveToSD();
}

bool SparseDistributedMemory::initialize() {
    Serial.println("Initializing SDM...");
    
    // Load config from SD card if available
    loadConfig();
    
    // Initialize memory structures
    addresses.clear();
    memory.clear();
    access_counts.clear();
    
    addresses.resize(config.num_locations);
    memory.resize(config.num_locations);
    access_counts.resize(config.num_locations, 0);
    
    // Generate random sparse addresses
    std::random_device rd;
    std::mt19937 gen(rd());
    
    for (uint16_t i = 0; i < config.num_locations; i++) {
        addresses[i].resize(config.vector_dim, 0);
        memory[i].resize(config.vector_dim, 0);
        
        // Generate sparse address (3% density as recommended)
        generateSparseVector(addresses[i], config.sparsity);
    }
    
    // Try to load existing memory from SD card
    if (!loadMemoryFromSD()) {
        Serial.println("No existing memory found, starting fresh");
    }
    
    Serial.printf("SDM initialized: %d locations, %d dimensions\n", 
                  config.num_locations, config.vector_dim);
    return true;
}

void SparseDistributedMemory::generateSparseVector(std::vector<uint8_t>& vector, float sparsity) {
    std::fill(vector.begin(), vector.end(), 0);
    
    uint16_t num_ones = static_cast<uint16_t>(config.vector_dim * sparsity);
    std::random_device rd;
    std::mt19937 gen(rd());
    
    // Randomly select positions to set to 1
    std::vector<uint16_t> indices(config.vector_dim);
    std::iota(indices.begin(), indices.end(), 0);
    std::shuffle(indices.begin(), indices.end(), gen);
    
    for (uint16_t i = 0; i < num_ones && i < indices.size(); i++) {
        vector[indices[i]] = 1;
    }
}

uint16_t SparseDistributedMemory::hammingDistance(const std::vector<uint8_t>& v1, const std::vector<uint8_t>& v2) {
    uint16_t distance = 0;
    for (size_t i = 0; i < v1.size() && i < v2.size(); i++) {
        if (v1[i] != v2[i]) distance++;
    }
    return distance;
}

uint16_t SparseDistributedMemory::write(const std::vector<uint8_t>& input_vector, uint8_t strength) {
    if (input_vector.size() != config.vector_dim) {
        Serial.println("Error: Input vector dimension mismatch");
        return 0;
    }
    
    uint16_t activated_locations = 0;
    
    for (uint16_t i = 0; i < config.num_locations; i++) {
        uint16_t dist = hammingDistance(input_vector, addresses[i]);
        
        if (dist <= config.access_radius) {
            activated_locations++;
            access_counts[i]++;
            
            // Update memory with reinforcement
            for (uint16_t j = 0; j < config.vector_dim; j++) {
                if (input_vector[j] == 1) {
                    int32_t updated = memory[i][j] + strength;
                    memory[i][j] = (updated > INT16_MAX) ? INT16_MAX : updated;
                } else {
                    int32_t updated = memory[i][j] - strength;
                    memory[i][j] = (updated < INT16_MIN) ? INT16_MIN : updated;
                }
            }
        }
    }
    
    stats.total_writes++;
    stats.last_activated_locations = activated_locations;
    
    return activated_locations;
}

std::pair<std::vector<uint8_t>, float> SparseDistributedMemory::read(const std::vector<uint8_t>& query_vector) {
    if (query_vector.size() != config.vector_dim) {
        Serial.println("Error: Query vector dimension mismatch");
        return {std::vector<uint8_t>(config.vector_dim, 0), 0.0f};
    }
    
    std::vector<uint16_t> activated_indices;
    std::vector<uint16_t> distances;
    
    // Find activated locations
    for (uint16_t i = 0; i < config.num_locations; i++) {
        uint16_t dist = hammingDistance(query_vector, addresses[i]);
        if (dist <= config.access_radius) {
            activated_indices.push_back(i);
            distances.push_back(dist);
        }
    }
    
    if (activated_indices.empty()) {
        return {std::vector<uint8_t>(config.vector_dim, 0), 0.0f};
    }
    
    // Weighted sum based on distance
    std::vector<float> total(config.vector_dim, 0.0f);
    float total_weight = 0.0f;
    
    for (size_t i = 0; i < activated_indices.size(); i++) {
        float weight = 1.0f / (1.0f + distances[i]);  // Closer = higher weight
        total_weight += weight;
        
        uint16_t loc_idx = activated_indices[i];
        for (uint16_t j = 0; j < config.vector_dim; j++) {
            total[j] += weight * memory[loc_idx][j];
        }
    }
    
    // Normalize and threshold
    std::vector<uint8_t> output(config.vector_dim);
    float max_confidence = 0.0f;
    
    for (uint16_t i = 0; i < config.vector_dim; i++) {
        float normalized_value = total[i] / total_weight;
        output[i] = (normalized_value > 0) ? 1 : 0;
        max_confidence = std::max(max_confidence, std::abs(normalized_value));
    }
    
    stats.total_reads++;
    stats.last_confidence = max_confidence;
    
    return {output, max_confidence};
}

bool SparseDistributedMemory::loadConfig() {
    if (!SD.exists(config.config_file)) {
        Serial.println("No config file found, using defaults");
        return false;
    }
    
    File file = SD.open(config.config_file);
    if (!file) {
        Serial.println("Failed to open config file");
        return false;
    }
    
    String content = file.readString();
    file.close();
    
    DynamicJsonDocument doc(1024);
    DeserializationError error = deserializeJson(doc, content);
    
    if (error) {
        Serial.println("Failed to parse config JSON");
        return false;
    }
    
    config.vector_dim = doc["vector_dim"] | config.vector_dim;
    config.num_locations = doc["num_locations"] | config.num_locations;
    config.access_radius = doc["access_radius"] | config.access_radius;
    config.sparsity = doc["sparsity"] | config.sparsity;
    
    Serial.println("Config loaded successfully");
    return true;
}

bool SparseDistributedMemory::saveConfig() {
    DynamicJsonDocument doc(1024);
    doc["vector_dim"] = config.vector_dim;
    doc["num_locations"] = config.num_locations;
    doc["access_radius"] = config.access_radius;
    doc["sparsity"] = config.sparsity;
    doc["timestamp"] = millis();
    
    File file = SD.open(config.config_file, FILE_WRITE);
    if (!file) {
        Serial.println("Failed to create config file");
        return false;
    }
    
    serializeJson(doc, file);
    file.close();
    
    Serial.println("Config saved successfully");
    return true;
}

bool SparseDistributedMemory::saveMemoryToSD() {
    // Create SDM directory if it doesn't exist
    if (!SD.exists("/sdm")) {
        SD.mkdir("/sdm");
    }
    
    File file = SD.open(memory_file, FILE_WRITE);
    if (!file) {
        Serial.println("Failed to create memory file");
        return false;
    }
    
    // Write header
    file.write((uint8_t*)&config.num_locations, sizeof(config.num_locations));
    file.write((uint8_t*)&config.vector_dim, sizeof(config.vector_dim));
    
    // Write access counts
    for (uint16_t i = 0; i < config.num_locations; i++) {
        file.write((uint8_t*)&access_counts[i], sizeof(access_counts[i]));
    }
    
    // Write memory data
    for (uint16_t i = 0; i < config.num_locations; i++) {
        for (uint16_t j = 0; j < config.vector_dim; j++) {
            file.write((uint8_t*)&memory[i][j], sizeof(memory[i][j]));
        }
    }
    
    file.close();
    Serial.println("Memory saved to SD card");
    return true;
}

bool SparseDistributedMemory::loadMemoryFromSD() {
    if (!SD.exists(memory_file)) {
        return false;
    }
    
    File file = SD.open(memory_file);
    if (!file) {
        return false;
    }
    
    // Read and verify header
    uint16_t stored_locations, stored_dim;
    file.read((uint8_t*)&stored_locations, sizeof(stored_locations));
    file.read((uint8_t*)&stored_dim, sizeof(stored_dim));
    
    if (stored_locations != config.num_locations || stored_dim != config.vector_dim) {
        Serial.println("Memory file dimension mismatch");
        file.close();
        return false;
    }
    
    // Read access counts
    for (uint16_t i = 0; i < config.num_locations; i++) {
        file.read((uint8_t*)&access_counts[i], sizeof(access_counts[i]));
    }
    
    // Read memory data
    for (uint16_t i = 0; i < config.num_locations; i++) {
        for (uint16_t j = 0; j < config.vector_dim; j++) {
            file.read((uint8_t*)&memory[i][j], sizeof(memory[i][j]));
        }
    }
    
    file.close();
    Serial.println("Memory loaded from SD card");
    return true;
}

bool SparseDistributedMemory::saveToSD() {
    bool success = true;
    success &= saveConfig();
    success &= saveMemoryToSD();
    success &= saveStatsToSD();
    return success;
}

bool SparseDistributedMemory::loadFromSD() {
    bool success = true;
    success &= loadConfig();
    success &= loadMemoryFromSD();
    return success;
}

bool SparseDistributedMemory::saveStatsToSD() {
    DynamicJsonDocument doc(1024);
    doc["total_writes"] = stats.total_writes;
    doc["total_reads"] = stats.total_reads;
    doc["last_confidence"] = stats.last_confidence;
    doc["last_activated_locations"] = stats.last_activated_locations;
    doc["avg_match_ratio"] = stats.avg_match_ratio;
    doc["timestamp"] = millis();
    
    File file = SD.open(stats_file, FILE_WRITE);
    if (!file) return false;
    
    serializeJson(doc, file);
    file.close();
    return true;
}

void SparseDistributedMemory::printMemoryUsage() {
    Serial.println("=== SDM Memory Usage ===");
    Serial.printf("Addresses: %d locations x %d dims = %d bytes\n", 
                  config.num_locations, config.vector_dim, 
                  config.num_locations * config.vector_dim);
    Serial.printf("Memory: %d locations x %d dims x 2 bytes = %d bytes\n", 
                  config.num_locations, config.vector_dim, 
                  config.num_locations * config.vector_dim * 2);
    Serial.printf("Access counts: %d x 2 bytes = %d bytes\n", 
                  config.num_locations, config.num_locations * 2);
    
    uint32_t total_bytes = config.num_locations * config.vector_dim * 3 + config.num_locations * 2;
    Serial.printf("Total SDM memory: %d bytes (%.1f KB)\n", total_bytes, total_bytes / 1024.0f);
    
    Serial.printf("Free heap: %d bytes\n", ESP.getFreeHeap());
    Serial.printf("Total heap: %d bytes\n", ESP.getHeapSize());
}