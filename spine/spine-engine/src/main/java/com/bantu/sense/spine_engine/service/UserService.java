package com.bantu.sense.spine_engine.service;

import com.bantu.sense.spine_engine.model.User;
import com.bantu.sense.spine_engine.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class UserService {

    @Autowired
    private UserRepository userRepository;

    public User registerUser(User user) {
        // Logic: Check if user already exists to avoid duplicates
        return userRepository.findByPhoneNumber(user.getPhoneNumber())
                .orElseGet(() -> userRepository.save(user));
    }

    public List<User> getAllUsers() {
        return userRepository.findAll();
    }
}