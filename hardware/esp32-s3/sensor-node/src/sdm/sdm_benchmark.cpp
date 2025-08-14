#include "sdm.h"

SDMBenchmark::SDMBenchmark() {
    // Initialize benchmark results directory
    if (!SD.exists("/sdm")) {
        SD.mkdir("/sdm");
    }
}

bool SDMBenchmark::runQuickBenchmark() {
    Serial.println("=== Running Quick SDM Benchmark ===");
    
    // Quick test with limited parameters to find baseline
    std::vector<uint16_t> quick_dims = {32, 64};
    std::vector<uint16_t> quick_locations = {100, 200};
    std::vector<float> quick_factors = {0.2f, 0.4f, 0.6f};
    
    float best_performance = 0.0f;
    SDMConfig best_config;
    
    File csvFile = SD.open(benchmark_results_file, FILE_WRITE);
    if (!csvFile) {
        Serial.println("Failed to open benchmark results file");
        return false;
    }
    
    // Write CSV header
    csvFile.println("vector_dim,num_locations,access_radius,radius_factor,reinforcement,match_ratio,confidence,duration_ms,memory_usage");
    
    uint16_t test_count = 0;
    uint16_t total_tests = quick_dims.size() * quick_locations.size() * quick_factors.size() * 3; // 3 reinforcement levels
    
    for (uint16_t dim : quick_dims) {
        for (uint16_t locations : quick_locations) {
            for (float factor : quick_factors) {
                for (uint8_t reinforce : {5, 15, 30}) {
                    test_count++;
                    
                    SDMConfig test_config;
                    test_config.vector_dim = dim;
                    test_config.num_locations = locations;
                    test_config.access_radius = static_cast<uint16_t>(dim * factor);
                    
                    Serial.printf("Test %d/%d: dim=%d, locs=%d, radius=%d, reinforce=%d\n", 
                                  test_count, total_tests, dim, locations, test_config.access_radius, reinforce);
                    
                    unsigned long start_time = millis();
                    float performance = testConfiguration(test_config, 5); // 5 test iterations
                    unsigned long duration = millis() - start_time;
                    
                    // Calculate memory usage
                    uint32_t memory_usage = locations * dim * 3 + locations * 2; // bytes
                    
                    // Log to CSV
                    String csv_line = String(dim) + "," + String(locations) + "," + 
                                      String(test_config.access_radius) + "," + String(factor, 2) + "," +
                                      String(reinforce) + "," + String(performance, 3) + "," +
                                      String(0.0f, 2) + "," + String(duration) + "," + String(memory_usage);
                    csvFile.println(csv_line);
                    csvFile.flush();
                    
                    if (performance > best_performance) {
                        best_performance = performance;
                        best_config = test_config;
                    }
                    
                    // Memory check
                    if (ESP.getFreeHeap() < 50000) { // Keep 50KB free
                        Serial.println("Memory getting low, stopping benchmark");
                        break;
                    }
                }
            }
        }
    }
    
    csvFile.close();
    
    Serial.printf("Best performance: %.3f with dim=%d, locations=%d, radius=%d\n", 
                  best_performance, best_config.vector_dim, best_config.num_locations, best_config.access_radius);
    
    // Save optimal config
    saveOptimalConfig(best_config);
    
    return true;
}

float SDMBenchmark::testConfiguration(const SDMConfig& config, uint8_t num_tests) {
    SparseDistributedMemory test_sdm(config);
    if (!test_sdm.initialize()) {
        return 0.0f;
    }
    
    float total_match_ratio = 0.0f;
    
    for (uint8_t test = 0; test < num_tests; test++) {
        // Generate random sparse test vector
        std::vector<uint8_t> test_vector(config.vector_dim, 0);
        uint16_t num_ones = static_cast<uint16_t>(config.vector_dim * config.sparsity);
        
        // Randomly set bits (ensure no duplicates)
        std::vector<uint16_t> indices;
        for (uint16_t i = 0; i < config.vector_dim; i++) {
            indices.push_back(i);
        }
        
        // Shuffle and take first num_ones elements
        for (uint16_t i = 0; i < num_ones && i < config.vector_dim; i++) {
            uint16_t swap_idx = random(config.vector_dim - i) + i;
            std::swap(indices[i], indices[swap_idx]);
            test_vector[indices[i]] = 1;
        }
        
        // Write pattern multiple times (reinforcement)
        for (uint8_t i = 0; i < 10; i++) {
            test_sdm.write(test_vector);
        }
        
        // Read back and calculate match ratio
        auto [output_vector, confidence] = test_sdm.read(test_vector);
        
        uint16_t matches = 0;
        for (uint16_t i = 0; i < config.vector_dim; i++) {
            if (test_vector[i] == output_vector[i]) {
                matches++;
            }
        }
        
        float match_ratio = static_cast<float>(matches) / config.vector_dim;
        total_match_ratio += match_ratio;
    }
    
    return total_match_ratio / num_tests;
}

bool SDMBenchmark::runComprehensiveBenchmark() {
    Serial.println("=== Running Comprehensive SDM Benchmark ===");
    Serial.println("Warning: This may take several hours!");
    
    BenchmarkParams params;
    uint32_t total_configs = params.vector_dims.size() * params.num_locations.size() * 
                             params.radius_factors.size() * params.reinforce_cycles.size();
    
    Serial.printf("Total configurations to test: %d\n", total_configs);
    Serial.printf("Estimated time: %.1f hours\n", total_configs * 30.0f / 3600.0f); // 30 sec per test
    
    File csvFile = SD.open("/sdm_comprehensive_benchmark.csv", FILE_WRITE);
    if (!csvFile) {
        Serial.println("Failed to create comprehensive benchmark file");
        return false;
    }
    
    csvFile.println("vector_dim,num_locations,access_radius,radius_factor,reinforcement,match_ratio,confidence,duration_ms,memory_usage,free_heap");
    
    uint32_t config_count = 0;
    float best_performance = 0.0f;
    SDMConfig best_config;
    
    for (uint16_t dim : params.vector_dims) {
        for (uint16_t locations : params.num_locations) {
            // Check memory constraints
            uint32_t required_memory = locations * dim * 3 + locations * 2;
            if (required_memory > (ESP.getFreeHeap() - 100000)) { // Keep 100KB free
                Serial.printf("Skipping dim=%d, locations=%d (insufficient memory)\n", dim, locations);
                continue;
            }
            
            for (float factor : params.radius_factors) {
                for (uint8_t reinforce : params.reinforce_cycles) {
                    config_count++;
                    
                    SDMConfig test_config;
                    test_config.vector_dim = dim;
                    test_config.num_locations = locations;
                    test_config.access_radius = static_cast<uint16_t>(dim * factor);
                    
                    Serial.printf("Config %d/%d: dim=%d, locs=%d, r=%d, reinforce=%d\n", 
                                  config_count, total_configs, dim, locations, test_config.access_radius, reinforce);
                    
                    unsigned long start_time = millis();
                    float performance = testConfiguration(test_config, 3); // 3 iterations for speed
                    unsigned long duration = millis() - start_time;
                    
                    uint32_t memory_usage = required_memory;
                    uint32_t free_heap = ESP.getFreeHeap();
                    
                    // Save result
                    String csv_line = String(dim) + "," + String(locations) + "," + 
                                      String(test_config.access_radius) + "," + String(factor, 2) + "," +
                                      String(reinforce) + "," + String(performance, 4) + "," +
                                      String(0.0f, 2) + "," + String(duration) + "," + 
                                      String(memory_usage) + "," + String(free_heap);
                    csvFile.println(csv_line);
                    csvFile.flush();
                    
                    if (performance > best_performance) {
                        best_performance = performance;
                        best_config = test_config;
                    }
                    
                    // Progress update every 20 configs
                    if (config_count % 20 == 0) {
                        Serial.printf("Progress: %d/%d (%.1f%%), Best: %.3f\n", 
                                      config_count, total_configs, 
                                      100.0f * config_count / total_configs, best_performance);
                    }
                }
            }
        }
    }
    
    csvFile.close();
    
    Serial.printf("Comprehensive benchmark complete!\n");
    Serial.printf("Best performance: %.3f\n", best_performance);
    Serial.printf("Best config: dim=%d, locations=%d, radius=%d\n", 
                  best_config.vector_dim, best_config.num_locations, best_config.access_radius);
    
    saveOptimalConfig(best_config);
    return true;
}

bool SDMBenchmark::runMemoryConstraintTest() {
    Serial.println("=== Running Memory Constraint Test ===");
    
    File csvFile = SD.open("/sdm_memory_test.csv", FILE_WRITE);
    if (!csvFile) return false;
    
    csvFile.println("vector_dim,num_locations,memory_required,free_heap_before,free_heap_after,initialization_success,test_performance");
    
    std::vector<uint16_t> test_dims = {32, 64, 128, 256, 512, 1024};
    std::vector<uint16_t> test_locations = {100, 500, 1000, 2000, 5000, 8000, 10000};
    
    for (uint16_t dim : test_dims) {
        for (uint16_t locations : test_locations) {
            uint32_t required_memory = locations * dim * 3 + locations * 2;
            uint32_t free_heap_before = ESP.getFreeHeap();
            
            Serial.printf("Testing dim=%d, locations=%d (%.1f KB required)\n", 
                          dim, locations, required_memory / 1024.0f);
            
            bool success = false;
            float performance = 0.0f;
            
            if (required_memory < (free_heap_before - 50000)) { // Keep 50KB free
                SDMConfig test_config;
                test_config.vector_dim = dim;
                test_config.num_locations = locations;
                test_config.access_radius = dim / 4; // 25% radius
                
                SparseDistributedMemory test_sdm(test_config);
                success = test_sdm.initialize();
                
                if (success) {
                    performance = testConfiguration(test_config, 2); // Quick test
                }
            }
            
            uint32_t free_heap_after = ESP.getFreeHeap();
            
            String csv_line = String(dim) + "," + String(locations) + "," + 
                              String(required_memory) + "," + String(free_heap_before) + "," +
                              String(free_heap_after) + "," + String(success ? 1 : 0) + "," + 
                              String(performance, 3);
            csvFile.println(csv_line);
            csvFile.flush();
            
            // Stop if we're running out of memory
            if (!success || free_heap_after < 30000) {
                Serial.printf("Memory limit reached at dim=%d, locations=%d\n", dim, locations);
                break;
            }
        }
    }
    
    csvFile.close();
    Serial.println("Memory constraint test complete");
    return true;
}

SDMConfig SDMBenchmark::findOptimalConfig() {
    // Try to load existing optimal config
    if (SD.exists(optimal_config_file)) {
        File file = SD.open(optimal_config_file);
        if (file) {
            String content = file.readString();
            file.close();
            
            DynamicJsonDocument doc(1024);
            if (deserializeJson(doc, content) == DeserializationError::Ok) {
                SDMConfig config;
                config.vector_dim = doc["vector_dim"];
                config.num_locations = doc["num_locations"];
                config.access_radius = doc["access_radius"];
                config.sparsity = doc["sparsity"];
                
                Serial.println("Loaded optimal config from file");
                return config;
            }
        }
    }
    
    // Skip benchmark for ESP32-S3, use safe defaults
    Serial.println("No optimal config found, using ESP32-S3 safe defaults");

    SDMConfig default_config;
    default_config.vector_dim = 16;        // Very small - only ~800 bytes
    default_config.num_locations = 50;    // Very small
    default_config.access_radius = 3;     // Small radius  
    default_config.sparsity = 0.03f;

    Serial.println("Using ESP32-S3 safe configuration");
    saveOptimalConfig(default_config);    // Save it to SD card
    return default_config;
}

bool SDMBenchmark::saveOptimalConfig(const SDMConfig& config) {
    DynamicJsonDocument doc(1024);
    doc["vector_dim"] = config.vector_dim;
    doc["num_locations"] = config.num_locations;
    doc["access_radius"] = config.access_radius;
    doc["sparsity"] = config.sparsity;
    doc["timestamp"] = millis();
    doc["version"] = "1.0";
    
    File file = SD.open(optimal_config_file, FILE_WRITE);
    if (!file) {
        Serial.println("Failed to save optimal config");
        return false;
    }
    
    serializeJson(doc, file);
    file.close();
    
    Serial.println("Optimal config saved successfully");
    return true;
}

void SDMBenchmark::logBenchmarkResult(const SDMConfig& config, float performance, float duration) {
    String csv_line = String(config.vector_dim) + "," + String(config.num_locations) + "," + 
                      String(config.access_radius) + "," + String(performance, 4) + "," + 
                      String(duration, 2) + "," + String(millis());
    
    appendToCSV(benchmark_results_file, csv_line);
}

bool SDMBenchmark::appendToCSV(const String& filename, const String& data) {
    File file = SD.open(filename, FILE_APPEND);
    if (!file) {
        Serial.printf("Failed to append to %s\n", filename.c_str());
        return false;
    }
    
    file.println(data);
    file.close();
    return true;
}