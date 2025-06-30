package com.example.privacy.test;

import java.util.Properties;
import java.sql.Connection;
import java.sql.DriverManager;

public class TestViolations {
    
    // VIOLATION: HardcodedEmail - test@example.com
    private static final String TEST_EMAIL = "test@example.com";
    
    // VIOLATION: HardcodedSecret - sk-1234567890abcdef
    private static final String API_KEY = "sk-1234567890abcdef";
    
    // VIOLATION: InsecureConnection - http://insecure-api.com/data
    private static final String API_URL = "http://insecure-api.com/data";
    
    // VIOLATION: HardcodedPassword - password123
    private static final String DB_PASSWORD = "password123";
    
    // VIOLATION: HardcodedSSN - 123-45-6789
    private static final String SSN = "123-45-6789";
    
    // VIOLATION: HardcodedCreditCard - 4111-1111-1111-1111
    private static final String CREDIT_CARD = "4111-1111-1111-1111";
    
    public void processUserData() {
        // VIOLATION: InsecureConnection - http://api.example.com
        String userData = fetchDataFromAPI("http://api.example.com/users");
        
        // VIOLATION: HardcodedEmail - admin@company.com
        sendEmail("admin@company.com", "User data processed");
        
        // VIOLATION: HardcodedSecret - secret_key_12345
        authenticateUser("user123", "secret_key_12345");
    }
    
    public void databaseConnection() {
        Properties props = new Properties();
        // VIOLATION: HardcodedPassword - db_password_123
        props.setProperty("password", "db_password_123");
        
        // VIOLATION: InsecureConnection - jdbc:mysql://localhost:3306
        String url = "jdbc:mysql://localhost:3306/database";
        
        try {
            Connection conn = DriverManager.getConnection(url, props);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    public void logSensitiveData() {
        // VIOLATION: LoggingSensitiveData - Logging SSN
        System.out.println("Processing SSN: " + SSN);
        
        // VIOLATION: LoggingSensitiveData - Logging credit card
        System.out.println("Credit card: " + CREDIT_CARD);
        
        // VIOLATION: LoggingSensitiveData - Logging API key
        System.out.println("Using API key: " + API_KEY);
    }
    
    private String fetchDataFromAPI(String url) {
        // Implementation would go here
        return "user data";
    }
    
    private void sendEmail(String email, String message) {
        // Implementation would go here
        System.out.println("Sending email to: " + email);
    }
    
    private void authenticateUser(String username, String secret) {
        // Implementation would go here
        System.out.println("Authenticating user: " + username);
    }
} 