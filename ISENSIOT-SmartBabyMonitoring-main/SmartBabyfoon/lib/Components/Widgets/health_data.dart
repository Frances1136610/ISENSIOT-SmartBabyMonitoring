import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';

class HealthData extends StatefulWidget {
  const HealthData({super.key});

  @override
  HealthDataState createState() => HealthDataState();
}

class HealthDataState extends State<HealthData> {

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Row(
        children: [
          Expanded(
            child: StreamBuilder<QuerySnapshot>(
                    stream: FirebaseFirestore.instance
                        .collection('presenceState')
                        .orderBy('timestamp', descending: true)
                        .limit(1)
                        .snapshots(),
                    builder: (context, snapshot) {
                      if (snapshot.connectionState == ConnectionState.waiting) {
                        return const Center(child: CircularProgressIndicator());
                      }
                      if (!snapshot.hasData || snapshot.data!.docs.isEmpty) {
                        return const Center(child: Text("No Data"));
                      }
                      var presenceDocument = snapshot.data!.docs.first;
                      var presenceValue = presenceDocument['value'];
                      var card = presenceValue == false ?
                      const Card(
                        color: Color(0xffc0c4d7),
                        child: SizedBox(
                          height: 140,
                          child: Center(
                              child: Text(
                                "No baby detected :(",
                                style: TextStyle(
                                  fontSize: 20,
                                  color: Colors.white,
                                ),
                                textAlign: TextAlign.center,
                              )
                          ),
                        ),
                      ) :
                      StreamBuilder<QuerySnapshot>(
                          stream: FirebaseFirestore.instance
                              .collection('ir')
                              .orderBy('timestamp', descending: true)
                              .limit(1)
                              .snapshots(),
                          builder: (context, snapshot) {
                            if (snapshot.connectionState ==
                                ConnectionState.waiting) {
                              return const Center(
                                  child: CircularProgressIndicator());
                            }
                            if (!snapshot.hasData ||
                                snapshot.data!.docs.isEmpty) {
                              return const Center(child: Text("No Data"));
                            }
                            var document = snapshot.data!.docs.first;
                            var value = document['value'];
                            var cardColor = value < 37.5 ? const Color(
                                0xffffdc61) : const Color(0xfff70059);
                            value = value.toStringAsFixed(1);

                            return Card(
                              color: cardColor,
                              child: SizedBox(
                                height: 140,
                                child: Column(
                                  children: [
                                    const Text(
                                      "Body Temperature",
                                      style: TextStyle(
                                        fontSize: 12.5,
                                        color: Colors.white,
                                      ),
                                      textAlign: TextAlign.center,
                                    ),
                                    Expanded(
                                        child: Row(
                                          children: [
                                            Expanded(
                                                child:
                                                Text(
                                                  "$value\u2103",
                                                  style: const TextStyle(
                                                    fontSize: 65,
                                                    color: Colors.white,
                                                  ),
                                                  textAlign: TextAlign.center,
                                                )
                                            ),
                                          ],
                                        )
                                    )
                                  ],
                                ),
                              ),
                            );
                          }
                      );
                      return card;
                    }
            ),
          ),
          Expanded(
            child: StreamBuilder<QuerySnapshot>(
                stream: FirebaseFirestore.instance
                    .collection('moistureState')
                    .orderBy('timestamp', descending: true)
                    .limit(1)
                    .snapshots(),
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) {
                    return const Center(child: CircularProgressIndicator());
                  }
                  if (!snapshot.hasData || snapshot.data!.docs.isEmpty) {
                    return const Center(child: Text("No Data"));
                  }
                  var document = snapshot.data!.docs.first;
                  var value = document['value'];
                  var cardColor = value == false ? const Color(0xffffdc61) : const Color(0xfff70059);
                  var accidentStatus = value == false ? 'All\nGood!' : 'Oh\nNo!';
                  var accidentIcon =  value == false ? const FaIcon(FontAwesomeIcons.thumbsUp, color: Colors.white, size: 90) : const FaIcon(FontAwesomeIcons.droplet, color: Colors.white, size: 90);

                  return StreamBuilder<QuerySnapshot>(
                      stream: FirebaseFirestore.instance
                          .collection('presenceState')
                          .orderBy('timestamp', descending: true)
                          .limit(1)
                          .snapshots(),
                      builder: (context, snapshot) {
                        if (snapshot.connectionState == ConnectionState.waiting) {
                          return const Center(child: CircularProgressIndicator());
                        }
                        if (!snapshot.hasData || snapshot.data!.docs.isEmpty) {
                          return const Center(child: Text("No Data"));
                        }
                        var document = snapshot.data!.docs.first;
                        var value = document['value'];
                        var card = value == false ?
                        const Card(
                          color: Color(0xffc0c4d7),
                          child: SizedBox(
                            height: 140,
                            child: Center(
                                child: Text(
                                  "No baby detected :(",
                                  style: TextStyle(
                                    fontSize: 20,
                                    color: Colors.white,
                                  ),
                                  textAlign: TextAlign.center,
                                )
                            ),
                          ),
                        ) :
                        Card(
                          color: cardColor,
                          child: SizedBox(
                            height: 140,
                            child: Column(
                              children: [
                                const Text(
                                  "Accidents",
                                  style: TextStyle(
                                    fontSize: 12.5,
                                    color: Colors.white,
                                  ),
                                  textAlign: TextAlign.center,
                                ),
                                Expanded(
                                  child: Row(
                                    children: [
                                      Expanded(
                                        child: Text(
                                          accidentStatus,
                                          style: const TextStyle(
                                            fontSize: 30,
                                            color: Colors.white,
                                          ),
                                          textAlign: TextAlign.center,
                                        ),
                                      ),
                                      Expanded(
                                        child:accidentIcon
                                      )
                                    ],
                                  ),
                                ),
                              ],
                            ),
                          )
                        );
                        return card;
                    }
                  );
              }
            ),
          )
        ],
      )
    );
  }
}