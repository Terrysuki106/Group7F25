import 'package:flutter/material.dart';

void main() {
  runApp(const SmartPilotApp());
}

class SmartPilotApp extends StatelessWidget {
  const SmartPilotApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: "SmartPilot",
      theme: ThemeData(
        scaffoldBackgroundColor: const Color(0xffF5ECFF), // soft lavender
        textTheme: const TextTheme(
          headlineMedium: TextStyle(
            fontSize: 26,
            fontWeight: FontWeight.bold,
            color: Colors.black87,
          ),
          bodyLarge: TextStyle(
            fontSize: 18,
            color: Colors.black54,
          ),
        ),
      ),
      home: const LoginScreen(),
    );
  }
}

//
// LOGIN SCREEN
//
class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text(
                "SmartPilot",
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: Color(0xff5A4FFF),
                ),
              ),
              const SizedBox(height: 40),

              // Email
              _inputField("Email"),

              const SizedBox(height: 14),

              // Password
              _inputField("Password", isPassword: true),

              const SizedBox(height: 25),

              // Login Button
              _mainButton("Login", () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const DashboardScreen()),
                );
              }),
            ],
          ),
        ),
      ),
    );
  }
}

Widget _inputField(String label, {bool isPassword = false}) {
  return Container(
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(14),
    ),
    child: TextField(
      obscureText: isPassword,
      decoration: InputDecoration(
        labelText: label,
        border: InputBorder.none,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
      ),
    ),
  );
}

Widget _mainButton(String text, VoidCallback onTap) {
  return SizedBox(
    width: double.infinity,
    child: ElevatedButton(
      style: ElevatedButton.styleFrom(
        backgroundColor: const Color(0xffE5D9FF),
        foregroundColor: Colors.black87,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(14),
        ),
        padding: const EdgeInsets.symmetric(vertical: 16),
      ),
      onPressed: onTap,
      child: Text(text, style: const TextStyle(fontSize: 18)),
    ),
  );
}

//
// DASHBOARD SCREEN
//
class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
          color: Colors.black87,
        ),
        title: const Text("Dashboard"),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Driver Score Card
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: const Color(0xffD8E9FF),
                borderRadius: BorderRadius.circular(20),
              ),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text("Driver Score",
                      style:
                          TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                  SizedBox(height: 10),
                  Text("86 / 100",
                      style:
                          TextStyle(fontSize: 32, fontWeight: FontWeight.bold)),
                ],
              ),
            ),

            const SizedBox(height: 32),

            _mainButton("View Trip History", () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const TripHistoryScreen()),
              );
            }),
            const SizedBox(height: 16),

            _mainButton("View Analytics", () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const AnalyticsScreen()),
              );
            }),
            const SizedBox(height: 16),

            _mainButton("Profile", () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const ProfileScreen()),
              );
            }),
          ],
        ),
      ),
    );
  }
}

//
// TRIP HISTORY SCREEN
//
class TripHistoryScreen extends StatelessWidget {
  const TripHistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
          color: Colors.black87,
        ),
        title: const Text("Trip History"),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: const [
            TripTile("Trip 1", "12 km"),
            TripTile("Trip 2", "8 km"),
            TripTile("Trip 3", "21 km"),
          ],
        ),
      ),
    );
  }
}

class TripTile extends StatelessWidget {
  final String title;
  final String distance;

  const TripTile(this.title, this.distance, {super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title,
              style:
                  const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          const SizedBox(height: 4),
          Text("Distance: $distance",
              style: const TextStyle(fontSize: 16, color: Colors.black54)),
        ],
      ),
    );
  }
}

//
// ANALYTICS SCREEN
//
class AnalyticsScreen extends StatelessWidget {
  const AnalyticsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
          color: Colors.black87,
        ),
        title: const Text("Analytics"),
      ),
      body: const Center(
        child: Text(
          "Analytics Graphs Coming Soon...",
          style: TextStyle(fontSize: 20, color: Colors.black54),
        ),
      ),
    );
  }
}

//
// PROFILE SCREEN
//
class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
          color: Colors.black87,
        ),
        title: const Text("Profile"),
      ),
      body: const Center(
        child: Text(
          "User Profile Details",
          style: TextStyle(fontSize: 20, color: Colors.black54),
        ),
      ),
    );
  }
}
