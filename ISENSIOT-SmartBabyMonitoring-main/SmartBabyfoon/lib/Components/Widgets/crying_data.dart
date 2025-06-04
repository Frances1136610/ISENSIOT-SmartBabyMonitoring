import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:intl/intl.dart';

class CryingData extends StatefulWidget {
  const CryingData({super.key});

  @override
  CryingDataState createState() => CryingDataState();
}

class CryingDataState extends State<CryingData> {

  String capitalize(String s) => s[0].toUpperCase() + s.substring(1);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: StreamBuilder<QuerySnapshot>(
          stream: FirebaseFirestore.instance
              .collection('babyEmotion')
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
            var isCrying = document['isCrying'];
            var cardColor = isCrying == false ? const Color(0xff6070ff) : const Color(0xfff70059);
            var cryingStatus = isCrying == false ? 'Happy' : capitalize(document['emotion']);
            var emotionIcon =  isCrying == false ? const FaIcon(FontAwesomeIcons.faceLaughBeam, color: Colors.white, size: 110) : const FaIcon(FontAwesomeIcons.faceSadCry, color: Colors.white, size: 110);
            var silentOrCrying = isCrying == false ? "Silent" : "Crying";
            DateTime timestamp = document['timestamp'].toDate();
            String formattedTimestamp = DateFormat('dd-MM-yyyy kk:mm').format(timestamp);

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
                      height: 146,
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
                    child: Padding(
                      padding: const EdgeInsets.all(10.0),
                      child: Row(
                        children: [
                          Expanded(
                            child: Center(
                              child: emotionIcon
                            )
                          ),
                          Expanded(
                            child: Padding(
                              padding: const EdgeInsets.all(8.0),
                              child: SizedBox(
                                height: 100,
                                child: Column(
                                  children: [
                                    Align(
                                      alignment: Alignment.topLeft,
                                      child: SizedBox(
                                        height: 46,
                                        child: FittedBox(
                                          child: Text(
                                              cryingStatus,
                                              style: const TextStyle(
                                                color: Colors.white,
                                                fontFamily: 'Montserrat'
                                              ),
                                          ),
                                        )
                                      ),
                                    ),
                                    Align(
                                      alignment: Alignment.topLeft,
                                      child: SizedBox(
                                        height: 46,
                                        child: Text(
                                          "$silentOrCrying since: \n$formattedTimestamp",
                                          style: const TextStyle(
                                            color: Colors.white,
                                            fontFamily: 'Montserrat',
                                            fontSize: 10,
                                          ),
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            )
                          ),
                        ],
                      ),
                    ),
                  );
                  return card;
              }
            );
        }
      )
    );
  }
}