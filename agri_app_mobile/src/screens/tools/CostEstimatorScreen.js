
import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { COLORS, SIZES, SHADOWS } from '../../constants/theme';
import Input from '../../components/Input';
import Button from '../../components/Button';

const CostEstimatorScreen = () => {
    const [area, setArea] = useState('');
    const [crop, setCrop] = useState('');
    const [cost, setCost] = useState(null);

    const calculateCost = () => {
        // Mock logic
        const baseCostPerAcre = {
            'rice': 15000,
            'wheat': 12000,
            'maize': 10000
        };
        const selectedCrop = crop.toLowerCase();
        let unitCost = baseCostPerAcre[selectedCrop] || 10000; // Default
        const total = parseFloat(area || 0) * unitCost;
        setCost(total);
    };

    return (
        <ScrollView style={styles.container}>
            <Text style={styles.title}>Cultivation Cost Estimator</Text>

            <View style={styles.form}>
                <Input
                    label="Land Area (Acres)"
                    placeholder="e.g. 2.5"
                    value={area}
                    onChangeText={setArea}
                    keyboardType="numeric"
                />
                <Input
                    label="Crop Name"
                    placeholder="e.g. Rice, Wheat"
                    value={crop}
                    onChangeText={setCrop}
                />

                <Button title="Estimate Cost" onPress={calculateCost} />

                {cost !== null && (
                    <View style={styles.resultContainer}>
                        <Text style={styles.resultLabel}>Estimated Total Cost:</Text>
                        <Text style={styles.resultAmount}>₹ {cost.toFixed(2)}</Text>
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
        marginBottom: SIZES.large,
    },
    form: {
        marginBottom: 20,
    },
    resultContainer: {
        marginTop: 30,
        backgroundColor: COLORS.white,
        padding: SIZES.medium,
        borderRadius: SIZES.radius,
        alignItems: 'center',
        ...SHADOWS.medium,
    },
    resultLabel: {
        fontSize: 16,
        color: COLORS.gray,
    },
    resultAmount: {
        fontSize: 32,
        fontWeight: 'bold',
        color: COLORS.success,
        marginTop: 10,
    }
});

export default CostEstimatorScreen;
