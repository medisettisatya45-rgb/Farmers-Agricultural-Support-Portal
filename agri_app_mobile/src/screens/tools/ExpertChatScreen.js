
import React, { useState } from 'react';
import { View, Text, StyleSheet, FlatList, TextInput, TouchableOpacity, KeyboardAvoidingView, Platform, Image } from 'react-native';
import { COLORS, SIZES, SHADOWS } from '../../constants/theme';
import { Send, User, MessageCircle } from 'lucide-react-native';

const initialMessages = [
    { id: '1', text: 'Hello! How can I help you today?', sender: 'expert', time: '10:00 AM' },
    { id: '2', text: 'My tomato plants have yellow leaves. What should I do?', sender: 'user', time: '10:05 AM' },
    { id: '3', text: 'Yellow leaves can be caused by nutrient deficiency or watering issues. Can you share a photo?', sender: 'expert', time: '10:07 AM' },
];

const ExpertChatScreen = () => {
    const [messages, setMessages] = useState(initialMessages);
    const [inputText, setInputText] = useState('');

    const sendMessage = () => {
        if (inputText.trim().length === 0) return;

        const newMessage = {
            id: Date.now().toString(),
            text: inputText,
            sender: 'user',
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };

        setMessages((prev) => [...prev, newMessage]);
        setInputText('');

        // Simulate expert reply
        setTimeout(() => {
            const reply = {
                id: (Date.now() + 1).toString(),
                text: 'Thank you for the details. I recommend checking your soil moisture levels first.',
                sender: 'expert',
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            };
            setMessages((prev) => [...prev, reply]);
        }, 1500);
    };

    const renderItem = ({ item }) => {
        const isUser = item.sender === 'user';
        return (
            <View style={[styles.messageBubble, isUser ? styles.userBubble : styles.expertBubble]}>
                {!isUser && (
                    <View style={styles.avatar}>
                        <User color={COLORS.white} size={16} />
                    </View>
                )}
                <View style={[styles.bubbleContent, isUser ? styles.userContent : styles.expertContent]}>
                    <Text style={[styles.messageText, isUser ? styles.userText : styles.expertText]}>
                        {item.text}
                    </Text>
                    <Text style={[styles.timeText, isUser ? styles.userTime : styles.expertTime]}>
                        {item.time}
                    </Text>
                </View>
            </View>
        );
    };

    return (
        <View style={styles.container}>
            <View style={styles.header}>
                <View style={styles.expertInfo}>
                    <View style={styles.expertAvatar}>
                        <MessageCircle color={COLORS.white} size={24} />
                    </View>
                    <View>
                        <Text style={styles.headerTitle}>Agri Expert</Text>
                        <Text style={styles.headerStatus}>Online</Text>
                    </View>
                </View>
            </View>

            <FlatList
                data={messages}
                renderItem={renderItem}
                keyExtractor={item => item.id}
                contentContainerStyle={styles.chatList}
                showsVerticalScrollIndicator={false}
            />

            <KeyboardAvoidingView
                behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
                keyboardVerticalOffset={90}
                style={styles.inputContainer}
            >
                <TextInput
                    style={styles.input}
                    placeholder="Type a message..."
                    value={inputText}
                    onChangeText={setInputText}
                    multiline
                />
                <TouchableOpacity style={styles.sendButton} onPress={sendMessage}>
                    <Send color={COLORS.white} size={20} />
                </TouchableOpacity>
            </KeyboardAvoidingView>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.background,
    },
    header: {
        padding: SIZES.medium,
        backgroundColor: COLORS.primary,
        ...SHADOWS.medium,
        paddingTop: SIZES.xlarge, // Extra padding for status bar if needed, handled by SafeArea usually
    },
    expertInfo: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    expertAvatar: {
        width: 40,
        height: 40,
        borderRadius: 20,
        backgroundColor: 'rgba(255,255,255,0.2)',
        justifyContent: 'center',
        alignItems: 'center',
        marginRight: SIZES.medium,
    },
    headerTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.white,
    },
    headerStatus: {
        fontSize: 12,
        color: '#E8F5E9',
    },
    chatList: {
        padding: SIZES.medium,
        paddingBottom: 80,
    },
    messageBubble: {
        flexDirection: 'row',
        marginBottom: SIZES.medium,
        alignItems: 'flex-end',
    },
    userBubble: {
        justifyContent: 'flex-end',
    },
    expertBubble: {
        justifyContent: 'flex-start',
    },
    avatar: {
        width: 30,
        height: 30,
        borderRadius: 15,
        backgroundColor: COLORS.secondary,
        justifyContent: 'center',
        alignItems: 'center',
        marginRight: 8,
    },
    bubbleContent: {
        maxWidth: '75%',
        padding: SIZES.medium,
        borderRadius: SIZES.radius,
        ...SHADOWS.small,
    },
    userContent: {
        backgroundColor: COLORS.primary,
        borderBottomRightRadius: 0,
    },
    expertContent: {
        backgroundColor: COLORS.white,
        borderBottomLeftRadius: 0,
    },
    messageText: {
        fontSize: 15,
        lineHeight: 20,
    },
    userText: {
        color: COLORS.white,
    },
    expertText: {
        color: COLORS.text,
    },
    timeText: {
        fontSize: 10,
        marginTop: 4,
        alignSelf: 'flex-end',
    },
    userTime: {
        color: 'rgba(255,255,255,0.7)',
    },
    expertTime: {
        color: COLORS.gray,
    },
    inputContainer: {
        flexDirection: 'row',
        padding: SIZES.medium,
        backgroundColor: COLORS.white,
        alignItems: 'center',
        borderTopWidth: 1,
        borderTopColor: '#EEEEEE',
    },
    input: {
        flex: 1,
        backgroundColor: '#F5F5F5',
        borderRadius: 20,
        paddingHorizontal: SIZES.medium,
        paddingVertical: 10,
        marginRight: SIZES.small,
        fontSize: 15,
        color: COLORS.text,
        maxHeight: 100,
    },
    sendButton: {
        width: 44,
        height: 44,
        borderRadius: 22,
        backgroundColor: COLORS.primary,
        justifyContent: 'center',
        alignItems: 'center',
        ...SHADOWS.small,
    }
});

export default ExpertChatScreen;
