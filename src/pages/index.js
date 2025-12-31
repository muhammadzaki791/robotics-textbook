import clsx from "clsx"
import Link from "@docusaurus/Link"
import useDocusaurusContext from "@docusaurus/useDocusaurusContext"
import Layout from "@theme/Layout"

import styles from "./index.module.css"

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext()
  return (
    <header className={clsx(styles.heroBanner)}>
      <div className={clsx("container", styles.heroContainer)}>
        <h1>{siteConfig.title}</h1>
        <p>{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link className={clsx("button", "button--lg", "button--secondary")} to="/docs/robotics-textbook/introduction">
            📖 Start Reading
          </Link>
          <Link className={clsx("button", "button--lg", "button--primary")} to="/docs">
            View Curriculum
          </Link>
        </div>
      </div>
    </header>
  )
}

function IntroductionSection() {
  return (
    <section className={styles.section}>
      <div className={clsx("container", styles.heroContainer)}>
        <p className={styles.description}>
          Welcome to the <strong>Physical AI & Humanoid Robotics Textbook</strong>—a comprehensive resource designed for
          undergraduate and advanced high-school students embarking on their robotics journey.
        </p>
        <p className={styles.description}>
          This textbook bridges the gap between theoretical foundations and practical applications, providing clear
          explanations of complex concepts with real-world relevance. Whether you're new to robotics or advancing your
          expertise, you'll find structured learning paths, hands-on exercises, and insights into cutting-edge research.
        </p>
      </div>
    </section>
  )
}

function FeaturesSection() {
  const features = [
    {
      title: "⚙️ Foundational Concepts",
      description:
        "Master kinematics, dynamics, and control systems that form the backbone of robotic motion, sensing, and intelligent behavior.",
    },
    {
      title: "👁️ Perception & Manipulation",
      description:
        "Explore robot vision, sensing technologies, manipulation strategies, and human-robot interaction principles for real-world applications.",
    },
    {
      title: "🧠 Intelligence & Ethics",
      description:
        "Discover machine learning in robotics, humanoid design principles, and ethical implications of autonomous AI systems.",
    },
  ]

  return (
    <section className={styles.section}>
      <div className="container">
        <h2 className={styles.sectionTitle}>What You'll Learn</h2>
        <p className={styles.sectionSubtitle}>Comprehensive coverage across three core pillars of modern robotics</p>
        <div className={clsx(styles.grid, styles["grid-3"])}>
          {features.map((feature, idx) => (
            <div key={idx} className={styles.featureCard}>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

function BenefitsSection() {
  const benefits = [
    "Theory meets practice with real-world robotics examples",
    "Progressive curriculum from fundamentals to advanced topics",
    "Hands-on exercises and design challenges",
    "Ethical frameworks for responsible AI development",
    "Current research and industry insights",
    "Interactive visualizations and simulations",
  ]

  return (
    <section className={styles.section}>
      <div className={clsx("container", styles.heroContainer)}>
        <h2 className={styles.sectionTitle}>Why This Textbook?</h2>
        <ul className={styles.benefitsList}>
          {benefits.map((benefit, idx) => (
            <li key={idx}>{benefit}</li>
          ))}
        </ul>
        <div style={{ textAlign: "center" }}>
          <Link className={styles.ctaButton} to="/docs/robotics-textbook/introduction">
            Begin Your Learning Journey →
          </Link>
        </div>
      </div>
    </section>
  )
}

export default function Home() {
  const { siteConfig } = useDocusaurusContext()
  return (
    <Layout
      title={`Welcome to ${siteConfig.title}`}
      description="A comprehensive textbook on Physical AI and Humanoid Robotics for undergraduate and advanced students"
    >
      <HomepageHeader />
      <main>
        <IntroductionSection />
        <FeaturesSection />
        <BenefitsSection />
      </main>
    </Layout>
  )
}
