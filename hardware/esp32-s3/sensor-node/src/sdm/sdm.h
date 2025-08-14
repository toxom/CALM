#ifndef SDM_H
#define SDM_H

#include <Arduino.h>
#include <vector>
#include <algorithm>
#include <numeric>
#include <SD.h>
#include <ArduinoJson.h>

struct SDMConfig {
    uint16_t vector_dim = 128;
    uint16_t num_locations = 1000;
    uint16_t access_radius = 20;
    float sparsity = 0.03f;  // 3% sparsity as recommended
    String config_file = "/sdm_config.json";
};

struct SDMStats {
    uint32_t total_writes = 0;
    uint32_t total_reads = 0;
    float last_confidence = 0.0f;
    uint16_t last_activated_locations = 0;
    float avg_match_ratio = 0.0f;
};

class SparseDistributedMemory {
private:
    SDMStats stats;
    
    // Memory storage - using dynamic allocation for ESP32
    std::vector<std::vector<uint8_t>> addresses;      // Hard locations
    std::vector<std::vector<int16_t>> memory;         // Signed counters
    std::vector<uint16_t> access_counts;              // Usage tracking
    
    // File paths
    String memory_file = "/sdm/memory.bin";
    String stats_file = "/sdm/stats.json";
    String lib_path = "/lib/";
    
    // Helper functions
    uint16_t hammingDistance(const std::vector<uint8_t>& v1, const std::vector<uint8_t>& v2);
    bool saveMemoryToSD();
    bool loadMemoryFromSD();
    void generateSparseVector(std::vector<uint8_t>& vector, float sparsity);
    
public:
    SDMConfig config;  // Make config public so benchmark can access it
    
    SparseDistributedMemory();
    SparseDistributedMemory(const SDMConfig& cfg);
    ~SparseDistributedMemory();
    
    // Core SDM operations
    bool initialize();
    uint16_t write(const std::vector<uint8_t>& input_vector, uint8_t strength = 1);
    std::pair<std::vector<uint8_t>, float> read(const std::vector<uint8_t>& query_vector);
    
    // Configuration management
    bool loadConfig();
    bool saveConfig();
    void updateConfigFromBenchmark(const String& benchmark_file);
    
    // Memory persistence
    bool saveToSD();
    bool loadFromSD();
    void clearMemory();
    
    // Pre-trained library management
    bool loadPretrainedLib(const String& lib_name);
    bool savePretrainedLib(const String& lib_name);
    std::vector<String> listPretrainedLibs();
    
    // Statistics and monitoring
    SDMStats getStats() const { return stats; }
    void resetStats();
    bool saveStatsToSD();
    
    // Utility functions
    void printMemoryUsage();
    bool testSDCardAccess();
};

// Encoder/Decoder for text and data
class SDMEncoder {
private:
    SparseDistributedMemory* sdm;
    uint16_t sequence_length = 32;  // Max sequence length
    
public:
    SDMEncoder(SparseDistributedMemory* sdm_instance);
    
    // Text encoding/decoding
    std::vector<uint8_t> encodeText(const String& text);
    String decodeText(const std::vector<uint8_t>& vector);
    
    // Numeric encoding
    std::vector<uint8_t> encodeFloat(float value, float min_val = -100.0f, float max_val = 100.0f);
    float decodeFloat(const std::vector<uint8_t>& vector, float min_val = -100.0f, float max_val = 100.0f);
    
    // Sequence encoding (for time series or multi-dimensional data)
    std::vector<uint8_t> encodeSequence(const std::vector<float>& sequence);
    std::vector<float> decodeSequence(const std::vector<uint8_t>& vector);
};

// Benchmark runner for ESP32-S3
class SDMBenchmark {
private:
    String benchmark_results_file = "/sdm_benchmark_results.csv";
    String optimal_config_file = "/sdm_optimal_config.json";
    
    struct BenchmarkParams {
        std::vector<uint16_t> vector_dims = {32, 64, 128, 256};
        std::vector<uint16_t> num_locations = {500, 1000, 2000};
        std::vector<float> radius_factors = {0.1f, 0.2f, 0.4f, 0.6f};
        std::vector<uint8_t> reinforce_cycles = {1, 5, 10, 20, 30};
    };
    
public:
    SDMBenchmark();
    
    // Run benchmarks
    bool runQuickBenchmark();         // Fast benchmark for basic optimization
    bool runComprehensiveBenchmark(); // Full parameter sweep
    bool runMemoryConstraintTest();   // Test ESP32-S3 memory limits
    
    // Results analysis
    SDMConfig findOptimalConfig();
    bool saveOptimalConfig(const SDMConfig& config);
    
    // Benchmark utilities
    float testConfiguration(const SDMConfig& config, uint8_t num_tests = 10);
    void logBenchmarkResult(const SDMConfig& config, float performance, float duration);
    bool appendToCSV(const String& filename, const String& data);
};

#endif