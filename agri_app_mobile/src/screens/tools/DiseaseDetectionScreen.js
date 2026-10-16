
import React, { useState } from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity, ScrollView, ActivityIndicator } from 'react-native';
import { COLORS, SIZES, SHADOWS } from '../../constants/theme';
import { Camera, Upload, AlertCircle, CheckCircle } from 'lucide-react-native';

const DiseaseDetectionScreen = ({ navigation }) => {
    const [image, setImage] = useState(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);

    const pickImage = async () => {
        // Mock image picker for demonstration as strict dependencies might not be installed
        // In production, use expo-image-picker
        setLoading(true);
        setTimeout(() => {
            setImage('https://via.placeholder.com/300x300.png?text=Crop+Image');
            setLoading(false);
            setResult(null); // Clear previous result
        }, 1000);
    };

    const analyzeImage = () => {
        if (!image) return;
        setLoading(true);
        // Mock analysis
        setTimeout(() => {
            setLoading(false);
            setResult({
                disease: 'Leaf Blight',
                confidence: '92%',
                treatment: 'Apply fungicide containing copper oxychloride. Ensure proper drainage and avoid overhead irrigation.',
                severity: 'Moderate'
            });
        }, 2000);
    };

    return (
        <ScrollView style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.title}>AI Disease Detection</Text>
                <Text style={styles.subtitle}>Upload a photo of your crop to detect diseases instantly.</Text>
            </View>

            <View style={styles.uploadSection}>
                {image ? (
                    <Image source={{ uri: image }} style={styles.previewImage} />
                ) : (
                    <View style={styles.placeholder}>
                        <Camera color={COLORS.gray} size={64} />
                        <Text style={styles.placeholderText}>No Image Selected</Text>
                    </View>
                )}

                <View style={styles.buttonRow}>
                    <TouchableOpacity style={styles.uploadButton} onPress={pickImage}>
                        <Upload color={COLORS.white} size={20} />
                        <Text style={styles.buttonText}>Upload Photo</Text>
                    </TouchableOpacity>
                    
                    {image && (
                        <TouchableOpacity 
                            style={[styles.analyzeButton, loading && styles.disabledButton]} 
                            onPress={analyzeImage}
                            disabled={loading}
                        >
                            {loading ? (
                                <ActivityIndicator color={COLORS.white} size="small" />
                            ) : (
                                <>
                                    <AlertCircle color={COLORS.white} size={20} />
                                    <Text style={styles.buttonText}>Analyze</Text>
                                </>
                            )}
                        </TouchableOpacity>
                    )}
                </View>
            </View>

            {loading && (
                <View style={styles.loadingContainer}>
                    <ActivityIndicator size="large" color={COLORS.primary} />
                    <Text style={styles.loadingText}>Analyzing crop health...</Text>
                </View>
            )}

            {result && !loading && (
                <View style={styles.resultCard}>
                    <View style={styles.resultHeader}>
                        <CheckCircle color={COLORS.success} size={24} />
                        <Text style={styles.resultTitle}>Analysis Complete</Text>
                    </View>
                    
                    <View style={styles.resultItem}>
                        <Text style={styles.label}>Detected Disease:</Text>
                        <Text style={styles.value}>{result.disease}</Text>
                    </View>
                    
                    <View style={styles.resultItem}>
                        <Text style={styles.label}>Confidence:</Text>
                        <Text style={styles.value}>{result.confidence}</Text>
                    </View>
                    
                    <View style={styles.resultItem}>
                        <Text style={styles.label}>Severity:</Text>
                        <Text style={[styles.value, { color: 'orange' }]}>{result.severity}</Text>
                    </View>

                    <View style={styles.divider} />

                    <Text style={styles.sectionHeader}>Recommended Treatment:</Text>
                    <Text style={styles.treatmentText}>{result.treatment}</Text>
                </View>
            )}
        </ScrollView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.background,
    },
    header: {
        padding: SIZES.large,
        backgroundColor: COLORS.white,
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        color: COLORS.primary,
        marginBottom: SIZES.small,
    },
    subtitle: {
        fontSize: 14,
        color: COLORS.gray,
        lineHeight: 20,
    },
    uploadSection: {
        padding: SIZES.large,
        alignItems: 'center',
    },
    placeholder: {
        width: '100%',
        height: 250,
        backgroundColor: '#E8F5E9',
        borderRadius: SIZES.radius,
        justifyContent: 'center',
        alignItems: 'center',
        borderWidth: 2,
        borderColor: '#C8E6C9',
        borderStyle: 'dashed',
        marginBottom: SIZES.large,
    },
    previewImage: {
        width: '100%',
        height: 250,
        borderRadius: SIZES.radius,
        marginBottom: SIZES.large,
    },
    placeholderText: {
        marginTop: SIZES.medium,
        color: COLORS.gray,
        fontSize: 16,
    },
    buttonRow: {
        flexDirection: 'row',
        gap: SIZES.medium,
        width: '100%',
        justifyContent: 'center',
    },
    uploadButton: {
        flexDirection: 'row',
        backgroundColor: COLORS.secondary,
        paddingVertical: 12,
        paddingHorizontal: 24,
        borderRadius: 25,
        alignItems: 'center',
        gap: 8,
        ...SHADOWS.small,
    },
    analyzeButton: {
        flexDirection: 'row',
        backgroundColor: COLORS.primary,
        paddingVertical: 12,
        paddingHorizontal: 24,
        borderRadius: 25,
        alignItems: 'center',
        gap: 8,
        ...SHADOWS.small,
    },
    disabledButton: {
        opacity: 0.7,
    },
    buttonText: {
        color: COLORS.white,
        fontWeight: 'bold',
        fontSize: 16,
    },
    loadingContainer: {
        padding: SIZES.large,
        alignItems: 'center',
    },
    loadingText: {
        marginTop: SIZES.small,
        color: COLORS.primary,
    },
    resultCard: {
        margin: SIZES.large,
        padding: SIZES.large,
        backgroundColor: COLORS.white,
        borderRadius: SIZES.radius,
        ...SHADOWS.medium,
    },
    resultHeader: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: SIZES.medium,
        gap: SIZES.small,
    },
    resultTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.success,
    },
    resultItem: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: SIZES.small,
    },
    label: {
        fontSize: 16,
        color: COLORS.text,
        fontWeight: '600',
    },
    value: {
        fontSize: 16,
        color: COLORS.dark,
    },
    divider: {
        height: 1,
        backgroundColor: '#E0E0E0',
        marginVertical: SIZES.medium,
    },
    sectionHeader: {
        fontSize: 16,
        fontWeight: 'bold',
        color: COLORS.text,
        marginBottom: SIZES.small,
    },
    treatmentText: {
        fontSize: 14,
        color: COLORS.dark,
        lineHeight: 22,
    }
});

export default DiseaseDetectionScreen;
