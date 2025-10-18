"""
Script para poblar la base de datos con datos de prueba.
Genera pacientes, consultas y estudios médicos con datos realistas.
"""

from datetime import date, datetime, timedelta
from random import choice, randint, random, uniform

from app.database import get_session
from app.models import Consultation, MedicalStudy, Patient, StudyType

# Datos argentinos realistas
NOMBRES = [
    "Juan",
    "María",
    "Carlos",
    "Ana",
    "José",
    "Laura",
    "Luis",
    "Sofía",
    "Miguel",
    "Lucía",
    "Diego",
    "Valentina",
    "Jorge",
    "Camila",
    "Ricardo",
    "Florencia",
    "Pablo",
    "Martina",
    "Gabriel",
    "Catalina",
    "Fernando",
    "Victoria",
    "Sergio",
    "Jimena",
    "Mateo",
    "Emma",
    "Nicolás",
    "Isabella",
]

APELLIDOS = [
    "González",
    "Rodríguez",
    "García",
    "López",
    "Martínez",
    "Fernández",
    "Pérez",
    "Sánchez",
    "Romero",
    "Silva",
    "Torres",
    "Álvarez",
    "Ruiz",
    "Díaz",
    "Moreno",
    "Gutiérrez",
    "Castro",
    "Vargas",
    "Ramírez",
    "Suárez",
]

MOTIVOS_CONSULTA = [
    "Control de rutina",
    "Dolor de cabeza persistente",
    "Gripe y fiebre",
    "Control de presión arterial",
    "Dolor abdominal",
    "Consulta por alergias",
    "Chequeo anual",
    "Seguimiento de tratamiento",
    "Dolor en articulaciones",
    "Problemas respiratorios",
    "Control de diabetes",
    "Consulta por lesión deportiva",
    "Examen pre-operatorio",
    "Control post-operatorio",
]

SINTOMAS = [
    "Dolor de cabeza intenso, náuseas ocasionales",
    "Fiebre de 38°C, malestar general, tos seca",
    "Dolor abdominal en región epigástrica, sin otros síntomas",
    "Presión alta, mareos leves",
    "Congestión nasal, estornudos frecuentes, picazón en los ojos",
    "Sin síntomas, control preventivo",
    "Dolor en rodilla derecha al caminar, inflamación leve",
    "Dificultad para respirar al hacer ejercicio",
    "Cansancio excesivo, sueño irregular",
    "Dolor muscular generalizado",
]

DIAGNOSTICOS = [
    "Cefalea tensional",
    "Gripe estacional (Influenza A)",
    "Gastritis leve",
    "Hipertensión arterial grado I",
    "Rinitis alérgica estacional",
    "Estado de salud normal",
    "Tendinitis rotuliana",
    "Asma leve",
    "Síndrome de fatiga crónica",
    "Fibromialgia leve",
]

TRATAMIENTOS = [
    "Paracetamol 500mg cada 8 horas por 5 días. Reposo.",
    "Ibuprofeno 400mg cada 8 horas por 7 días. Antihistamínico 10mg por día.",
    "Omeprazol 20mg antes del desayuno por 14 días. Dieta blanda.",
    "Enalapril 10mg por día. Control en 15 días.",
    "Loratadina 10mg por día. Evitar alérgenos.",
    "Mantener hábitos saludables. Control anual.",
    "Antiinflamatorios tópicos. Fisioterapia 3 veces por semana.",
    "Salbutamol inhalador según necesidad. Seguimiento en 30 días.",
    "Complejo vitamínico B. Mejorar higiene del sueño.",
    "Analgésicos leves. Ejercicio de bajo impacto.",
]

TIPOS_SANGRE = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

ALERGIAS = [
    None,
    "Penicilina",
    "Aspirina",
    "Polen",
    "Ácaros del polvo",
    "Mariscos",
    "Frutos secos",
]

CONDICIONES_CRONICAS = [
    None,
    "Hipertensión arterial",
    "Diabetes tipo 2",
    "Asma",
    "Hipotiroidismo",
    "Artritis",
]


def generar_dni() -> str:
    """Genera un DNI argentino realista (7-8 dígitos)"""
    return str(randint(20000000, 45000000))


def generar_telefono() -> str:
    """Genera un teléfono argentino realista"""
    codigo_area = choice(["011", "221", "351", "341", "261", "223"])
    numero = randint(1000000, 9999999)
    return f"+54 {codigo_area} {numero}"


def generar_email(nombre: str, apellido: str) -> str:
    """Genera un email realista"""
    dominios = ["gmail.com", "hotmail.com", "yahoo.com.ar", "outlook.com"]
    return f"{nombre.lower()}.{apellido.lower()}@{choice(dominios)}"


def generar_direccion() -> str:
    """Genera una dirección argentina realista"""
    calles = [
        "Av. Corrientes",
        "Av. Santa Fe",
        "Calle Florida",
        "Av. 9 de Julio",
        "Av. Rivadavia",
        "Calle Lavalle",
        "Av. Callao",
        "Calle Sarmiento",
        "Av. Belgrano",
        "Calle Tucumán",
    ]
    return f"{choice(calles)} {randint(100, 9999)}, Buenos Aires"


def poblar_pacientes(session, cantidad: int = 20) -> list[Patient]:
    """Crea pacientes de prueba"""
    pacientes = []

    for _ in range(cantidad):
        nombre = choice(NOMBRES)
        apellido = choice(APELLIDOS)

        # Edad aleatoria entre 18 y 85 años
        edad = randint(18, 85)
        fecha_nacimiento = date.today() - timedelta(days=edad * 365)

        paciente = Patient(
            first_name=nombre,
            last_name=apellido,
            dni=generar_dni(),
            birth_date=fecha_nacimiento,
            gender=choice(["M", "F"]),
            blood_type=choice(TIPOS_SANGRE),
            phone=generar_telefono(),
            email=generar_email(nombre, apellido),
            address=generar_direccion(),
            allergies=choice(ALERGIAS),
            chronic_conditions=choice(CONDICIONES_CRONICAS),
            is_active=random() > 0.1,  # 90% activos
        )

        session.add(paciente)
        pacientes.append(paciente)

    session.commit()
    print(f"✅ {len(pacientes)} pacientes creados")
    return pacientes


def poblar_consultas(session, pacientes: list[Patient], cantidad_por_paciente: int = 3):
    """Crea consultas de prueba para cada paciente"""
    total_consultas = 0

    for paciente in pacientes:
        # Número aleatorio de consultas (1-5)
        num_consultas = randint(1, cantidad_por_paciente + 2)

        for i in range(num_consultas):
            # Consultas en los últimos 6 meses
            dias_atras = randint(1, 180)
            fecha_consulta = datetime.now() - timedelta(days=dias_atras)

            consulta = Consultation(
                patient_id=paciente.id,
                consultation_date=fecha_consulta,
                reason=choice(MOTIVOS_CONSULTA),
                symptoms=choice(SINTOMAS) if random() > 0.2 else None,
                diagnosis=choice(DIAGNOSTICOS) if random() > 0.1 else None,
                treatment=choice(TRATAMIENTOS) if random() > 0.1 else None,
                # Signos vitales (70% tienen al menos algunos)
                blood_pressure=f"{randint(110, 140)}/{randint(70, 90)}" if random() > 0.3 else None,
                heart_rate=randint(60, 100) if random() > 0.3 else None,
                temperature=round(uniform(36.0, 37.8), 1) if random() > 0.3 else None,
                weight=round(uniform(50, 100), 1) if random() > 0.4 else None,
                height=round(uniform(150, 190), 0) if random() > 0.4 else None,
                notes=f"Paciente en buen estado general. {'Seguimiento programado.' if random() > 0.5 else 'Sin observaciones adicionales.'}"
                if random() > 0.5
                else None,
                # 30% tienen próxima visita programada
                next_visit=(date.today() + timedelta(days=randint(15, 90)))
                if random() > 0.7
                else None,
            )

            session.add(consulta)
            total_consultas += 1

    session.commit()
    print(f"✅ {total_consultas} consultas creadas")


def poblar_estudios(session, pacientes: list[Patient], cantidad: int = 30):
    """Crea estudios médicos de prueba"""
    estudios_creados = 0

    # Tipos de estudios más comunes
    tipos_estudios = [
        (StudyType.LABORATORY.value, "Análisis de sangre completo"),
        (StudyType.LABORATORY.value, "Perfil lipídico"),
        (StudyType.LABORATORY.value, "Glucemia"),
        (StudyType.RADIOLOGY.value, "Radiografía de tórax"),
        (StudyType.RADIOLOGY.value, "Radiografía de rodilla"),
        (StudyType.ULTRASOUND.value, "Ecografía abdominal"),
        (StudyType.ELECTROCARDIOGRAM.value, "Electrocardiograma"),
        (StudyType.TOMOGRAPHY.value, "Tomografía computada de cráneo"),
    ]

    for _ in range(cantidad):
        paciente = choice(pacientes)
        tipo, nombre = choice(tipos_estudios)

        # Estudios en los últimos 12 meses
        dias_atras = randint(1, 365)
        fecha_estudio = date.today() - timedelta(days=dias_atras)

        estudio = MedicalStudy(
            patient_id=paciente.id,
            study_type=tipo,
            study_name=nombre,
            study_date=fecha_estudio,
            institution=choice(
                [
                    "Hospital Italiano",
                    "Hospital Alemán",
                    "Sanatorio Güemes",
                    "Centro Médico Rossi",
                    "Clínica Bazterrica",
                ]
            ),
            requesting_doctor=f"Dr. {choice(APELLIDOS)}",
            results="Valores dentro de parámetros normales"
            if random() > 0.2
            else "Se observan algunas alteraciones menores",
            observations="Estudio realizado sin inconvenientes" if random() > 0.5 else None,
            is_pending=random() > 0.7,  # 30% pendientes
            is_critical=random() > 0.9,  # 10% críticos
            requires_followup=random() > 0.7,  # 30% requieren seguimiento
        )

        session.add(estudio)
        estudios_creados += 1

    session.commit()
    print(f"✅ {estudios_creados} estudios médicos creados")


def main():
    """Función principal para poblar la base de datos"""
    print("🚀 Iniciando población de base de datos...")
    print("=" * 60)

    session = next(get_session())

    try:
        # Verificar si ya hay datos
        pacientes_existentes = session.query(Patient).count()

        if pacientes_existentes > 0:
            respuesta = input(
                f"\n⚠️  Ya existen {pacientes_existentes} pacientes en la BD. ¿Agregar más datos? (s/N): "
            )
            if respuesta.lower() != "s":
                print("❌ Operación cancelada")
                return

        print("\n📊 Creando datos de prueba...\n")

        # Crear pacientes
        pacientes = poblar_pacientes(session, cantidad=20)

        # Crear consultas
        poblar_consultas(session, pacientes, cantidad_por_paciente=3)

        # Crear estudios médicos
        poblar_estudios(session, pacientes, cantidad=30)

        print("\n" + "=" * 60)
        print("✅ ¡Base de datos poblada exitosamente!")
        print("\n📈 Resumen:")
        print(f"   - Pacientes: {session.query(Patient).count()}")
        print(f"   - Consultas: {session.query(Consultation).count()}")
        print(f"   - Estudios: {session.query(MedicalStudy).count()}")
        print("\n🌐 Accede a http://localhost:3000 para ver los datos")

    except Exception as e:
        print(f"\n❌ Error al poblar la base de datos: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    main()
