#include "sdm.h"

// Pre-trained library management for SDM
class SDMPretrainedLib {
private:
    String lib_base_path = "/lib/";
    SparseDistributedMemory* sdm;
    
    struct LibraryInfo {
        String name;
        String description;
        uint32_t vector_count;
        uint32_t file_size;
        String creation_date;
    };
    
public:
    SDMPretrainedLib(SparseDistributedMemory* sdm_instance) : sdm(sdm_instance) {
        // Ensure lib directory exists
        if (!SD.exists(lib_base_path)) {
            SD.mkdir(lib_base_path);
        }
    }
    
    bool savePretrainedVectors(const String& lib_name, 
                               const std::vector<std::vector<uint8_t>>& vectors,
                               const std::vector<String>& labels = {}) {
        String lib_path = lib_base_path + lib_name + "/";
        
        // Create library directory
        if (!SD.exists(lib_path)) {
            SD.mkdir(lib_path);
        }
        
        // Save vectors in binary format
        String vectors_file = lib_path + "vectors.bin";
        File file = SD.open(vectors_file, FILE_WRITE);
        if (!file) {
            Serial.println("Failed to create vectors file");
            return false;
        }
        
        // Write header
        uint32_t num_vectors = vectors.size();
        uint32_t vector_dim = vectors.empty() ? 0 : vectors[0].size();
        file.write((uint8_t*)&num_vectors, sizeof(num_vectors));
        file.write((uint8_t*)&vector_dim, sizeof(vector_dim));
        
        // Write vectors
        for (const auto& vector : vectors) {
            for (uint8_t bit : vector) {
                file.write(&bit, 1);
            }
        }
        file.close();
        
        // Save labels if provided
        if (!labels.empty()) {
            String labels_file = lib_path + "labels.txt";
            File labelFile = SD.open(labels_file, FILE_WRITE);
            if (labelFile) {
                for (const String& label : labels) {
                    labelFile.println(label);
                }
                labelFile.close();
            }
        }
        
        // Save library metadata
        saveLibraryMetadata(lib_name, num_vectors, file.size());
        
        Serial.printf("Saved %d vectors to library '%s'\n", num_vectors, lib_name.c_str());
        return true;
    }
    
    bool loadPretrainedVectors(const String& lib_name,
                               std::vector<std::vector<uint8_t>>& vectors,
                               std::vector<String>& labels) {
        String lib_path = lib_base_path + lib_name + "/";
        String vectors_file = lib_path + "vectors.bin";
        
        if (!SD.exists(vectors_file)) {
            Serial.println("Library not found: " + lib_name);
            return false;
        }
        
        File file = SD.open(vectors_file);
        if (!file) {
            Serial.println("Failed to open vectors file");
            return false;
        }
        
        // Read header
        uint32_t num_vectors, vector_dim;
        file.read((uint8_t*)&num_vectors, sizeof(num_vectors));
        file.read((uint8_t*)&vector_dim, sizeof(vector_dim));
        
        // Validate dimensions
        if (vector_dim != sdm->config.vector_dim) {
            Serial.printf("Dimension mismatch: lib=%d, sdm=%d\n", vector_dim, sdm->config.vector_dim);
            file.close();
            return false;
        }
        
        // Read vectors
        vectors.clear();
        vectors.reserve(num_vectors);
        
        for (uint32_t i = 0; i < num_vectors; i++) {
            std::vector<uint8_t> vector(vector_dim);
            for (uint32_t j = 0; j < vector_dim; j++) {
                file.read(&vector[j], 1);
            }
            vectors.push_back(vector);
        }
        file.close();
        
        // Load labels if available
        String labels_file = lib_path + "labels.txt";
        labels.clear();
        if (SD.exists(labels_file)) {
            File labelFile = SD.open(labels_file);
            if (labelFile) {
                while (labelFile.available()) {
                    String label = labelFile.readStringUntil('\n');
                    label.trim();
                    if (label.length() > 0) {
                        labels.push_back(label);
                    }
                }
                labelFile.close();
            }
        }
        
        Serial.printf("Loaded %d vectors from library '%s'\n", vectors.size(), lib_name.c_str());
        return true;
    }
    
    bool mergeLibraryIntoSDM(const String& lib_name, uint8_t reinforcement = 3) {
        std::vector<std::vector<uint8_t>> vectors;
        std::vector<String> labels;
        
        if (!loadPretrainedVectors(lib_name, vectors, labels)) {
            return false;
        }
        
        Serial.printf("Merging %d vectors into SDM...\n", vectors.size());
        
        for (const auto& vector : vectors) {
            for (uint8_t i = 0; i < reinforcement; i++) {
                sdm->write(vector, 2); // Medium strength reinforcement
            }
        }
        
        Serial.println("Library merged successfully");
        return true;
    }
    
    std::vector<String> listAvailableLibraries() {
        std::vector<String> libraries;
        
        File root = SD.open(lib_base_path);
        if (!root) return libraries;
        
        while (true) {
            File entry = root.openNextFile();
            if (!entry) break;
            
            if (entry.isDirectory()) {
                String lib_name = entry.name();
                // Check if it contains vectors.bin
                String vectors_file = lib_base_path + lib_name + "/vectors.bin";
                if (SD.exists(vectors_file)) {
                    libraries.push_back(lib_name);
                }
            }
            entry.close();
        }
        root.close();
        
        return libraries;
    }
    
    bool createCommonWordsLibrary() {
        // Create a basic library of common English words
        std::vector<String> common_words = {
            "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HER", "WAS", "ONE",
            "OUR", "HAD", "BY", "WORD", "WHAT", "SAY", "EACH", "SHE", "WHICH", "DO", "HOW",
            "THEIR", "TIME", "WILL", "ABOUT", "IF", "UP", "OUT", "MANY", "THEN", "THEM",
            "THESE", "SO", "SOME", "HIM", "HAS", "TWO", "MORE", "VERY", "GO", "NO", "WAY",
            "COULD", "MY", "THAN", "FIRST", "WATER", "BEEN", "CALL", "WHO", "AM", "ITS",
            "NOW", "FIND", "LONG", "DOWN", "DAY", "DID", "GET", "COME", "MADE", "MAY", "PART"
        };
        
        std::vector<std::vector<uint8_t>> vectors;
        SDMEncoder encoder(sdm);
        
        for (const String& word : common_words) {
            auto encoded = encoder.encodeText(word);
            vectors.push_back(encoded);
        }
        
        return savePretrainedVectors("common_words", vectors, common_words);
    }
    
    bool createNumbersLibrary() {
        // Create a library for numbers 0-100
        std::vector<String> numbers;
        std::vector<std::vector<uint8_t>> vectors;
        SDMEncoder encoder(sdm);
        
        for (int i = 0; i <= 100; i++) {
            String num_str = String(i);
            numbers.push_back(num_str);
            auto encoded = encoder.encodeText(num_str);
            vectors.push_back(encoded);
        }
        
        return savePretrainedVectors("numbers", vectors, numbers);
    }
    
    void printLibraryInfo(const String& lib_name) {
        String lib_path = lib_base_path + lib_name + "/";
        String info_file = lib_path + "info.json";
        
        if (!SD.exists(info_file)) {
            Serial.println("No info available for library: " + lib_name);
            return;
        }
        
        File file = SD.open(info_file);
        if (file) {
            String content = file.readString();
            Serial.println("Library Info:");
            Serial.println(content);
            file.close();
        }
    }
    
private:
    bool saveLibraryMetadata(const String& lib_name, uint32_t vector_count, uint32_t file_size) {
        String lib_path = lib_base_path + lib_name + "/";
        String info_file = lib_path + "info.json";
        
        DynamicJsonDocument doc(1024);
        doc["name"] = lib_name;
        doc["vector_count"] = vector_count;
        doc["file_size"] = file_size;
        doc["vector_dim"] = sdm->config.vector_dim;
        doc["creation_time"] = millis();
        doc["version"] = "1.0";
        
        File file = SD.open(info_file, FILE_WRITE);
        if (!file) return false;
        
        serializeJson(doc, file);
        file.close();
        return true;
    }
};

// Add library management to SDM class
bool SparseDistributedMemory::loadPretrainedLib(const String& lib_name) {
    SDMPretrainedLib prelib(this);
    return prelib.mergeLibraryIntoSDM(lib_name);
}

bool SparseDistributedMemory::savePretrainedLib(const String& lib_name) {
    // Extract current SDM state as a library
    // This is a simplified version - in practice, you'd want to save
    // the most frequently accessed patterns
    
    SDMPretrainedLib prelib(this);
    std::vector<std::vector<uint8_t>> vectors;
    std::vector<String> labels;
    
    // Find most accessed memory locations and extract their patterns
    for (uint16_t i = 0; i < config.num_locations; i++) {
        if (access_counts[i] > 5) { // Only save frequently accessed patterns
            std::vector<uint8_t> pattern(config.vector_dim);
            for (uint16_t j = 0; j < config.vector_dim; j++) {
                pattern[j] = (memory[i][j] > 0) ? 1 : 0;
            }
            vectors.push_back(pattern);
            labels.push_back("pattern_" + String(i) + "_access_" + String(access_counts[i]));
        }
    }
    
    return prelib.savePretrainedVectors(lib_name, vectors, labels);
}

std::vector<String> SparseDistributedMemory::listPretrainedLibs() {
    SDMPretrainedLib prelib(this);
    return prelib.listAvailableLibraries();
}