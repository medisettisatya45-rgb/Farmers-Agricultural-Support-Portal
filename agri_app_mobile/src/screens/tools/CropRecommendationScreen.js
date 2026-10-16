
import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, Alert, Picker } from 'react-native';
import { COLORS, SIZES } from '../../constants/theme';
import Button from '../../components/Button';
import Input from '../../components/Input';

const CropRecommendationScreen = () => {
    const [nitrogen, setNitrogen] = useState('');
    const [phosphorus, setPhosphorus] = useState('');
    const [potassium, setPotassium] = useState('');
    const [ph, setPh] = useState('');
    const [rainfall, setRainfall] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);

    const handlePredict = async () => {
        setLoading(true);
        // Simulate API call or use actual if available
        // const response = await api.post('/predict_crop', { ... });
        setTimeout(() => {
            setLoading(false);
            setResult('Rice (Recommended based on conditions)');
            Alert.alert('Prediction Result', 'Recommended Crop: Rice');
        }, 1500);
    };

    return (
        <ScrollView style={styles.container}>
            <Text style={styles.title}>Crop Recommendation</Text>
            <Text style={styles.subtitle}>Enter soil and weather details to get the best crop advice.</Text>

            <View style={styles.form}>
                <Input
                    label="Nitrogen (N)"
                    placeholder="e.g. 90"
                    value={nitrogen}
                    onChangeText={setNitrogen}
                    keyboardType="numeric"
                />
                <Input
                    label="Phosphorus (P)"
                    placeholder="e.g. 42"
                    value={phosphorus}
                    onChangeText={setPhosphorus}
                    keyboardType="numeric"
                />
                <Input
                    label="Potassium (K)"
                    placeholder="e.g. 43"
                    value={potassium}
                    onChangeText={setPotassium}
                    keyboardType="numeric"
                />
                <Input
                    label="pH Level"
                    placeholder="e.g. 6.5"
                    value={ph}
                    onChangeText={setPh}
                    keyboardType="numeric"
                />
                <Input
                    label="Rainfall (mm)"
                    placeholder="e.g. 200"
                    value={rainfall}
                    onChangeText={setRainfall}
                    keyboardType="numeric"
                />

                <Button
                    title={loading ? "Analyzing..." : "Get Recommendation"}
                    onPress={handlePredict}
                    disabled={loading}
                    style={{ marginTop: 20 }}
                />

                {result && (
                    <View style={styles.resultContainer}>
                        <Text style={styles.resultLabel}>Recommended Crop:</Text>
                        <Text style={styles.resultText}>{result}</Text>
                    </View>
                )}
            </View>
        </ScrollView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.background,
        padding: SIZES.medium,
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        color: COLORS.primary,
        marginBottom: SIZES.small,
    },
    subtitle: {
        fontSize: 16,
        color: COLORS.gray,
        marginBottom: SIZES.large,
    },
    form: {
        marginBottom: 40,
    },
    resultContainer: {
        marginTop: 30,
        padding: SIZES.medium,
        backgroundColor: COLORS.tertiary,
        borderRadius: SIZES.radius,
        alignItems: 'center',
    },
    resultLabel: {
        fontSize: 18,
        color: COLORS.text,
    },
    resultText: {
        fontSize: 28,
        fontWeight: 'bold',
        color: COLORS.primary,
        marginTop: 10,
    }
});

export default CropRecommendationScreen;
