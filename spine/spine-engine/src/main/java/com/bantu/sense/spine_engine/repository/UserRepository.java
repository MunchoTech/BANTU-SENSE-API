package com.bantu.sense.spine_engine.repository;

import com.bantu.sense.spine_engine.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    // Custom "Magic Spell": Find a user by their phone number
    Optional<User> findByPhoneNumber(String phoneNumber);
}