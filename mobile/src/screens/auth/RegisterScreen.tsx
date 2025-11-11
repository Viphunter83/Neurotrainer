/**
 * RegisterScreen.tsx
 *
 * Экран регистрации с валидацией.
 */

import React, { useState, useCallback, useMemo, useRef } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Text,
  SafeAreaView,
  Keyboard,
  Animated,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { registerUser, clearError } from '../../store/slices/authSlice';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import {
  COLORS,
  SPACING,
  TYPOGRAPHY,
  BORDER_RADIUS,
} from '../../styles/theme';
import { validateEmail, validatePassword, validateUsername } from '../../utils/validators';

interface FormErrors {
  email?: string;
  username?: string;
  password?: string;
  confirmPassword?: string;
}

interface FormValues {
  email: string;
  username: string;
  password: string;
  confirmPassword: string;
  fullName: string;
}

interface RegisterScreenProps {
  navigation: any;
}

const RegisterScreen: React.FC<RegisterScreenProps> = ({ navigation }) => {
  const dispatch = useAppDispatch();
  const { isLoading, error } = useAppSelector((state) => state.auth);

  const [formValues, setFormValues] = useState<FormValues>({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    fullName: '',
  });
  const [formErrors, setFormErrors] = useState<FormErrors>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(50)).current;

  const validateField = useCallback(
    (field: string, value: string): string | undefined => {
      switch (field) {
        case 'email':
          return validateEmail(value) ? undefined : 'Invalid email address';
        case 'username':
          return validateUsername(value)
            ? undefined
            : 'Username must be 3-50 characters (alphanumeric and underscore)';
        case 'password':
          return validatePassword(value)
            ? undefined
            : 'Password must be at least 8 characters and contain uppercase, lowercase, digit, and special character';
        case 'confirmPassword':
          return value === formValues.password
            ? undefined
            : 'Passwords do not match';
        default:
          return undefined;
      }
    },
    [formValues.password],
  );

  const handleFieldChange = useCallback(
    (field: keyof FormValues, value: string) => {
      setFormValues((prev) => ({ ...prev, [field]: value }));
      if (touched[field]) {
        const error = validateField(field, value);
        setFormErrors((prev) => ({ ...prev, [field]: error }));
      }
    },
    [touched, validateField],
  );

  const handleFieldBlur = useCallback(
    (field: string) => {
      setTouched((prev) => ({ ...prev, [field]: true }));
      const error = validateField(
        field,
        formValues[field as keyof FormValues] as string,
      );
      setFormErrors((prev) => ({ ...prev, [field]: error }));
    },
    [formValues, validateField],
  );

  const isFormValid = useMemo(() => {
    return (
      validateEmail(formValues.email) &&
      validateUsername(formValues.username) &&
      validatePassword(formValues.password) &&
      formValues.password === formValues.confirmPassword &&
      !isLoading &&
      Object.keys(formErrors).length === 0
    );
  }, [formValues, formErrors, isLoading]);

  const handleRegister = useCallback(async () => {
    const newErrors: FormErrors = {};
    if (!validateEmail(formValues.email)) {
      newErrors.email = 'Invalid email address';
    }
    if (!validateUsername(formValues.username)) {
      newErrors.username = 'Invalid username';
    }
    if (!validatePassword(formValues.password)) {
      newErrors.password = 'Invalid password';
    }
    if (formValues.password !== formValues.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    if (Object.keys(newErrors).length > 0) {
      setFormErrors(newErrors);
      setTouched({
        email: true,
        username: true,
        password: true,
        confirmPassword: true,
      });
      return;
    }

    const result = await dispatch(
      registerUser({
        email: formValues.email,
        username: formValues.username,
        password: formValues.password,
        full_name: formValues.fullName || undefined,
      }),
    );

    if (result.type === 'auth/register/fulfilled') {
      // Navigate to login
      navigation.replace('Login');
    }
  }, [formValues, dispatch, navigation]);

  const handleNavigateToLogin = useCallback(() => {
    Keyboard.dismiss();
    navigation.replace('Login');
  }, [navigation]);

  React.useEffect(() => {
    return () => {
      dispatch(clearError());
    };
  }, [dispatch]);

  React.useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 300,
        useNativeDriver: true,
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 300,
        useNativeDriver: true,
      }),
    ]).start();
  }, [fadeAnim, slideAnim]);

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
        >
          <Animated.View
            style={[
              styles.content,
              {
                opacity: fadeAnim,
                transform: [{ translateY: slideAnim }],
              },
            ]}
          >
            <Text style={styles.title}>Create Account</Text>
            <Text style={styles.subtitle}>
              Sign up to start your fitness journey
            </Text>

            {error && (
              <View style={styles.errorContainer}>
                <Text style={styles.errorText}>{error}</Text>
              </View>
            )}

            <Input
              label="Email"
              placeholder="Enter your email"
              value={formValues.email}
              onChangeText={(value) => handleFieldChange('email', value)}
              onBlur={() => handleFieldBlur('email')}
              error={formErrors.email}
              keyboardType="email-address"
              autoCapitalize="none"
              autoComplete="email"
            />

            <Input
              label="Username"
              placeholder="Choose a username"
              value={formValues.username}
              onChangeText={(value) => handleFieldChange('username', value)}
              onBlur={() => handleFieldBlur('username')}
              error={formErrors.username}
              autoCapitalize="none"
              autoComplete="username"
            />

            <Input
              label="Full Name (Optional)"
              placeholder="Enter your full name"
              value={formValues.fullName}
              onChangeText={(value) => handleFieldChange('fullName', value)}
              autoCapitalize="words"
            />

            <Input
              label="Password"
              placeholder="Create a password"
              value={formValues.password}
              onChangeText={(value) => handleFieldChange('password', value)}
              onBlur={() => handleFieldBlur('password')}
              error={formErrors.password}
              secureTextEntry
              autoCapitalize="none"
            />

            <Input
              label="Confirm Password"
              placeholder="Confirm your password"
              value={formValues.confirmPassword}
              onChangeText={(value) =>
                handleFieldChange('confirmPassword', value)
              }
              onBlur={() => handleFieldBlur('confirmPassword')}
              error={formErrors.confirmPassword}
              secureTextEntry
              autoCapitalize="none"
            />

            <Button
              title="Sign Up"
              onPress={handleRegister}
              disabled={!isFormValid}
              isLoading={isLoading}
              style={styles.button}
            />

            <View style={styles.footer}>
              <Text style={styles.footerText}>Already have an account? </Text>
              <TouchableOpacity onPress={handleNavigateToLogin}>
                <Text style={styles.footerLink}>Sign In</Text>
              </TouchableOpacity>
            </View>
          </Animated.View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    padding: SPACING.lg,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
  },
  title: {
    ...TYPOGRAPHY.h1,
    color: COLORS.textDark,
    marginBottom: SPACING.sm,
    textAlign: 'center',
  },
  subtitle: {
    ...TYPOGRAPHY.body,
    color: COLORS.textSecondary,
    marginBottom: SPACING.xl,
    textAlign: 'center',
  },
  errorContainer: {
    backgroundColor: COLORS.error + '20',
    padding: SPACING.md,
    borderRadius: BORDER_RADIUS.md,
    marginBottom: SPACING.md,
  },
  errorText: {
    ...TYPOGRAPHY.caption,
    color: COLORS.error,
    textAlign: 'center',
  },
  button: {
    marginTop: SPACING.md,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: SPACING.lg,
  },
  footerText: {
    ...TYPOGRAPHY.body,
    color: COLORS.textSecondary,
  },
  footerLink: {
    ...TYPOGRAPHY.bodyBold,
    color: COLORS.primary,
  },
});

export default RegisterScreen;

